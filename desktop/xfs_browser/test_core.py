import io
import os
import struct
import tempfile
import threading
import unittest
import zlib
from pathlib import Path
from xfs_core import *

def n(value,size):return value.to_bytes(size,'little')
def chunk(data,flags=0):
    if flags==1:return n((flags<<22)|len(data),3)+b'\0\0'+data
    compressed=zlib.compress(data)
    if flags==2:return n((flags<<22)|len(data),3)+n(len(compressed),3)+b'\0\0'+compressed
    return n(len(compressed),3)+b'\0\0'+compressed

def make_archive(path,files,version=1,padding=0,large=False):
    offset=16;blocks=[];entries=[]
    for name,data,flags in files:
        block=chunk(data,flags);blocks.append(block);entries.append((name,offset,len(data),len(block)));offset+=len(block)
    if version==1:
        def record(name,off,size,packed,children=0,isfile=1):
            name=name.encode();return n(children,4)+n(len(name),1)+name+n(off,6)+n(size,4)+n(packed,4)+n(isfile,1)
        table=record('Root',0,0,0,len(entries),0)+b''.join(record(*e) for e in entries)+b'\0'*padding
        header_count=len(entries)+1
    else:
        table=b''.join(e[0].encode().ljust(112,b'\0')+struct.pack('<4I',e[1],1,e[2],e[3]) for e in entries);header_count=len(entries)
    header=bytearray(64);header[:4]=b'XFS '+b'' if version==1 else b'XFS2';header[8:12]=n(header_count,4)
    compressed_header=zlib.compress(header);compressed_table=zlib.compress(table)
    if large:offset=0x100000100
    with path.open('wb') as out:
        out.write(n(offset,6 if large else 4));out.seek(16)
        for block in blocks:out.write(block)
        out.seek(offset);out.write(n(len(compressed_header),1)+compressed_header)
        if version==1:out.write(n(len(table),3))
        out.write(n(len(compressed_table),3)+compressed_table)
    return path

class ReaderTests(unittest.TestCase):
    def setUp(self):self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()
    def test_both_versions_and_chunk_encodings(self):
        files=[('a.ltb',b'native-model'*500,0),('b.dtx',b'texture'*600,1),('folder/c.txt',b'hello'*300,2)]
        for version in (1,2):
            path=make_archive(self.root/f'v{version}.xfs',files,version)
            source_hash=__import__('hashlib').sha256(path.read_bytes()).hexdigest()
            archive=open_archive(path);self.assertEqual(len(archive.entries),3)
            dest=self.root/f'out{version}'
            for entry,(_,expected,_) in zip(archive.entries,files):
                self.assertEqual(extract_entry(archive,entry,dest),'written')
                target=safe_target(dest,entry.path);self.assertEqual(target.read_bytes(),expected)
                target.write_bytes(b'KEEP');self.assertEqual(extract_entry(archive,entry,dest),'skipped');self.assertEqual(target.read_bytes(),b'KEEP')
            self.assertEqual(__import__('hashlib').sha256(path.read_bytes()).hexdigest(),source_hash)
    def test_zero_padding(self):
        archive=open_archive(make_archive(self.root/'padding.xfs',[('a.ltb',b'abc',1)],padding=4881))
        self.assertEqual(archive.table_padding,4881)
    def test_sparse_over_4gb(self):
        archive=open_archive(make_archive(self.root/'large.xfs',[('a.ltb',b'abc',1)],large=True))
        self.assertGreater(archive.size,0xFFFFFFFF)
        extract_entry(archive,archive.entries[0],self.root/'out')
        self.assertEqual((self.root/'out/Root/a.ltb').read_bytes(),b'abc')
    def test_filter_and_cancel(self):
        entries=[Entry('Root/Pedro_Wolf.LTB',0,1,1),Entry('Root/pedro.dtx',0,1,1),Entry('Root/other.ltb',0,1,1)]
        self.assertEqual(filter_entries(entries,'PEDRO wolf','ltb'),[0])
        self.assertEqual(filter_entries(entries,'pedro','.dtx'),[1])
        stop=threading.Event();stop.set()
        with self.assertRaises(Cancelled):filter_entries(entries,cancel=stop)
    def test_windows_unsafe_paths(self):
        for name in ['../bad','Root/../../bad','C:/bad','/bad','Root/CON.ltb','Root/bad:name','Root/end.','Root//bad']:
            with self.subTest(name=name),self.assertRaises(XFSError):safe_target(self.root,name)
    def test_symlink_escape(self):
        if os.name=='nt':self.skipTest('Windows symlinks require special privileges')
        (self.root/'link').symlink_to(self.root.parent,target_is_directory=True)
        with self.assertRaises(XFSError):safe_target(self.root,'link/escape')
    def test_corrupt_and_changed_archive(self):
        path=make_archive(self.root/'test.xfs',[('a.ltb',b'abc',1)])
        archive=open_archive(path);path.write_bytes(path.read_bytes()+b'x')
        with self.assertRaises(XFSError):extract_entry(archive,archive.entries[0],self.root/'out')
        path.write_bytes(b'garbage')
        with self.assertRaises(XFSError):open_archive(path)
    def test_cancel_removes_partial_file(self):
        path=make_archive(self.root/'test.xfs',[('a.ltb',b'a'*60000,0)])
        archive=open_archive(path);stop=threading.Event()
        def progress(*_):stop.set()
        with self.assertRaises(Cancelled):extract_entry(archive,archive.entries[0],self.root/'out',stop,progress)
        self.assertFalse(list((self.root/'out').rglob('*.part')))
        self.assertFalse((self.root/'out/Root/a.ltb').exists())
    def test_oversized_decompression_rejected(self):
        with self.assertRaises(XFSError):inflate(zlib.compress(b'x'*10000),10)
    def test_40k_index_benchmark(self):
        import time
        files=[(f'pedro_{i:05}.ltb' if i%2 else f'pedro_{i:05}.dtx',b'x',1) for i in range(40000)]
        path=make_archive(self.root/'many.xfs',files)
        start=time.perf_counter();archive=open_archive(path);index_ms=1000*(time.perf_counter()-start)
        start=time.perf_counter();indices=filter_entries(archive.entries,'pedro','.ltb');search_ms=1000*(time.perf_counter()-start)
        self.assertEqual(len(indices),20000)
        print(f'BENCHMARK 40000 files: index={index_ms:.1f}ms filter={search_ms:.1f}ms')
    def test_preview_bound_and_csv(self):
        archive=open_archive(make_archive(self.root/'test.xfs',[('a.txt',b'hello',1)]))
        self.assertEqual(preview(archive,archive.entries[0]),b'hello')
        self.assertIsNone(preview(archive,archive.entries[0],limit=2))
        save_list(archive,[0],self.root/'list.csv')
        self.assertIn('Root/a.txt',(self.root/'list.csv').read_text(encoding='utf-8-sig'))

if __name__=='__main__':unittest.main(verbosity=2)
