"""Read-only Xenesis XFS / XFS2 reader. No game process or archive writes.
Format reference: Luigi Auriemma's xenesis.bms. See README.md.
"""
from __future__ import annotations
import csv
import os
import re
import struct
import tempfile
import threading
import zlib
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath
from typing import Callable

MAX_TABLE = 128 * 1024 * 1024
MAX_ENTRIES = 1_000_000
MAX_PATH = 4096

class XFSError(Exception):
    pass

class Cancelled(XFSError):
    pass

def check_cancel(event):
    if event is not None and event.is_set():
        raise Cancelled('İşlem iptal edildi.')

def read_exact(stream, count):
    data = stream.read(count)
    if len(data) != count:
        raise XFSError('Dosya beklenenden önce bitti.')
    return data

def uint(stream, size):
    return int.from_bytes(read_exact(stream, size), 'little')

def inflate(data, limit):
    if not 0 <= limit <= MAX_TABLE:
        raise XFSError('Açılacak veri güvenli bellek sınırını aşıyor.')
    try:
        decoder = zlib.decompressobj()
        result = decoder.decompress(data, limit + 1)
    except zlib.error as exc:
        raise XFSError(f'Sıkıştırılmış veri açılamadı: {exc}') from exc
    if len(result) > limit or decoder.unconsumed_tail or not decoder.eof:
        raise XFSError('Sıkıştırılmış veri boyutu veya bitişi geçersiz.')
    # Patched archives can leave zero padding following the zlib stream.
    if decoder.unused_data.strip(b'\0'):
        raise XFSError('Sıkıştırılmış veriden sonra bilinmeyen veri var.')
    return result

@dataclass(frozen=True, slots=True)
class Entry:
    path: str
    offset: int
    size: int
    packed: int
    @property
    def extension(self):
        return PureWindowsPath(self.path).suffix.casefold()

@dataclass(frozen=True, slots=True)
class Archive:
    path: Path
    version: str
    entries: tuple[Entry, ...]
    size: int
    mtime_ns: int
    table_padding: int = 0
    declared_entries: int = 0

class Cursor:
    def __init__(self, data):
        self.data = memoryview(data)
        self.pos = 0
    def read(self, n):
        if n < 0 or self.pos + n > len(self.data):
            raise XFSError('XFS dosya tablosu eksik veya bozuk.')
        start = self.pos
        self.pos += n
        return self.data[start:self.pos]
    def number(self, n):
        return int.from_bytes(self.read(n), 'little')

def decode_name(data):
    raw = bytes(data).split(b'\0', 1)[0]
    try:
        return raw.decode('utf-8')
    except UnicodeDecodeError:
        return raw.decode('cp1254')

def open_archive(path, cancel=None, progress=None):
    path = Path(path).resolve()
    stat = path.stat()
    entries = []
    with path.open('rb') as stream:
        offset = uint(stream, 6 if stat.st_size > 0xFFFFFFFF else 4)
        if offset < stream.tell() or offset >= stat.st_size:
            raise XFSError('XFS tablo konumu geçersiz. Bu paket sürümü desteklenmiyor olabilir.')
        stream.seek(offset)
        header_size = uint(stream, 1)
        header = inflate(read_exact(stream, header_size), 64)
        if len(header) != 64 or header[:3] != b'XFS':
            raise XFSError('Xenesis XFS başlığı bulunamadı.')
        version = header[3:4]
        declared = int.from_bytes(header[8:12], 'little')
        if declared > MAX_ENTRIES:
            raise XFSError('Dosya tablosu kayıt sınırını aşıyor.')
        if version == b' ':
            expected, packed = uint(stream, 3), uint(stream, 3)
        elif version == b'2':
            packed, expected = uint(stream, 3), declared * 128
        else:
            raise XFSError(f'Desteklenmeyen XFS sürümü: {version.hex()}')
        if expected > MAX_TABLE or packed > MAX_TABLE:
            raise XFSError('Dosya tablosu 128 MiB sınırını aşıyor.')
        check_cancel(cancel)
        table = inflate(read_exact(stream, packed), expected)
        if len(table) != expected:
            raise XFSError('Açılmış dosya tablosu boyutu eşleşmiyor.')
    cursor = Cursor(table)
    records = 0
    def add(name, off, size, packed_size):
        if len(name) > MAX_PATH or '\0' in name:
            raise XFSError('Geçersiz arşiv yolu.')
        if off < 0 or off + packed_size > stat.st_size:
            raise XFSError(f'Dosya arşiv sınırını aşıyor: {name}')
        entries.append(Entry(name, off, size, packed_size))
    if version == b' ':
        # Iterative depth-first walk: nesting cannot overflow Python recursion.
        pending = [('', 1)]
        while pending:
            prefix, count = pending[-1]
            if not count:
                pending.pop()
                continue
            pending[-1] = (prefix, count - 1)
            children = cursor.number(4)
            name = decode_name(cursor.read(cursor.number(1)))
            off, size, packed_size, is_file = cursor.number(6), cursor.number(4), cursor.number(4), cursor.number(1)
            full = (prefix + '/' + name).replace('\\', '/').lstrip('/')
            records += 1
            if records > MAX_ENTRIES or children > MAX_ENTRIES or len(pending) > 256:
                raise XFSError('XFS ağaç sınırı aşıldı.')
            if is_file:
                add(full, off, size, packed_size)
            if children:
                pending.append((full, children))
            if records % 512 == 0:
                check_cancel(cancel)
                if progress:
                    progress(records, max(declared, records))
    else:
        for _ in range(declared):
            name = decode_name(cursor.read(112)).replace('\\', '/').lstrip('/')
            off = cursor.number(4)
            cursor.number(4)
            add(name, off, cursor.number(4), cursor.number(4))
            records += 1
            if records % 512 == 0:
                check_cancel(cancel)
                if progress:
                    progress(records, declared)
    remainder = bytes(cursor.data[cursor.pos:])
    if remainder.strip(b'\0'):
        raise XFSError('Dosya tablosunun sonunda bilinmeyen kayıt var; arşiv değiştirilmedi.')
    check_cancel(cancel)
    return Archive(path, '1' if version == b' ' else '2', tuple(entries), stat.st_size,
                   stat.st_mtime_ns, len(remainder), declared)

def filter_entries(entries, query='', extension='', cancel=None):
    words = query.casefold().split()
    extension = extension.casefold().strip()
    if extension and not extension.startswith('.'):
        extension = '.' + extension
    result = []
    for index, entry in enumerate(entries):
        if index % 512 == 0:
            check_cancel(cancel)
        if extension and entry.extension != extension:
            continue
        name = entry.path.casefold()
        if all(word in name for word in words):
            result.append(index)
    return result

def safe_target(root, name):
    win = PureWindowsPath(name)
    if win.is_absolute() or win.drive or name.startswith(('/', '\\')):
        raise XFSError('Mutlak çıktı yolu reddedildi.')
    parts = name.replace('\\', '/').split('/')
    for part in parts:
        if (part in ('', '.', '..') or re.search(r'[<>:"|?*\x00-\x1f]', part)
                or part.endswith((' ', '.')) or re.fullmatch(r'(?i)(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?', part)):
            raise XFSError(f'Windows için geçersiz çıktı yolu: {name}')
    root = Path(root).resolve()
    target = root.joinpath(*parts).resolve()
    if not target.is_relative_to(root):
        raise XFSError('Çıktı yolu seçili klasörün dışına çıkıyor.')
    return target

def ensure_unchanged(archive):
    stat = archive.path.stat()
    if stat.st_size != archive.size or stat.st_mtime_ns != archive.mtime_ns:
        raise XFSError('Arşiv açıldıktan sonra değişmiş. Yeniden açın.')

def extract_entry(archive, entry, destination, cancel=None, progress=None):
    ensure_unchanged(archive)
    target = safe_target(destination, entry.path)
    if target.exists():
        return 'skipped'
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix='.xfs-', suffix='.part', dir=target.parent)
    try:
        written = 0
        with os.fdopen(descriptor, 'wb') as output, archive.path.open('rb') as source:
            source.seek(entry.offset)
            end = entry.offset + entry.packed
            while source.tell() < end:
                check_cancel(cancel)
                word = uint(source, 3)
                flags, count = word >> 22, word & 0x3FFFFF
                compressed = count
                if flags & 2 and not flags & 1:
                    compressed = uint(source, 3)
                if flags == 0:
                    count = 0x10000
                read_exact(source, 2)
                payload_size = count if flags & 1 else compressed
                if source.tell() + payload_size > end:
                    raise XFSError('Dosya bloğu kayıt sınırını aşıyor.')
                payload = read_exact(source, payload_size)
                data = payload if flags & 1 else inflate(payload, count)
                keep = min(len(data), max(0, entry.size - written))
                if keep:
                    output.write(memoryview(data)[:keep])
                    written += keep
                if progress:
                    progress(written, entry.size)
            if source.tell() != end or written != entry.size:
                raise XFSError('Çıkarılan dosyanın boyutu eşleşmiyor.')
        check_cancel(cancel)
        # Never replace an existing file, including one created during extraction.
        try:
            (os.rename if os.name == 'nt' else os.link)(temporary, target)
        except FileExistsError:
            return 'skipped'
        except OSError as exc:
            raise XFSError('Çıktı dosyası güvenle oluşturulamadı; klasörün yazılabilir olduğunu kontrol edin.') from exc
        return 'written'
    finally:
        Path(temporary).unlink(missing_ok=True)

def preview(archive, entry, limit=256 * 1024, cancel=None):
    # Use a temporary destination and normal validated extraction for small files.
    if entry.size > limit:
        return None
    with tempfile.TemporaryDirectory(prefix='xfs-preview-') as directory:
        extract_entry(archive, entry, directory, cancel)
        return safe_target(directory, entry.path).read_bytes()

def save_list(archive, indices, path):
    with open(path, 'w', encoding='utf-8-sig', newline='') as output:
        writer = csv.writer(output)
        writer.writerow(['path', 'extension', 'size_bytes', 'packed_bytes', 'offset'])
        for index in indices:
            e = archive.entries[index]
            writer.writerow([e.path, e.extension, e.size, e.packed, e.offset])
