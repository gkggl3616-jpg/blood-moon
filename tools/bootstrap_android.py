"""Download checksum-verified Android platform/build tools from Google's SDK repository."""
from pathlib import Path
import hashlib
import os
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / 'tools/cache'
BASE = 'https://dl.google.com/android/repository/'

def fetch(url, path):
    if path.exists():
        return
    print('Downloading', path.name, flush=True)
    partial = path.with_suffix(path.suffix + '.part')
    with urllib.request.urlopen(url, timeout=45) as response, partial.open('wb') as output:
        while data := response.read(1024 * 1024):
            output.write(data)
    partial.rename(path)

def child(element, name):
    return next((x for x in element if x.tag.split('}')[-1] == name), None)

def install(repo, package, folder):
    target = CACHE / folder
    if (target / '.complete').exists():
        print('Using cached', package, flush=True)
        return
    entry = next(e for e in repo if e.tag.split('}')[-1] == 'remotePackage' and e.get('path') == package)
    archives = child(entry, 'archives')
    for archive in archives:
        host = child(archive, 'host-os')
        if host is not None and host.text != 'linux':
            continue
        complete = child(archive, 'complete')
        name = child(complete, 'url').text
        checksum = child(complete, 'checksum')
        download = CACHE / Path(name).name
        fetch(BASE + name, download)
        actual = hashlib.sha1(download.read_bytes()).hexdigest()
        if actual != checksum.text.strip():
            raise RuntimeError('SDK archive checksum mismatch: ' + name)
        target.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(download) as z:
            # Google SDK archives contain a single top-level directory.
            for item in z.infolist():
                parts = Path(item.filename).parts[1:]
                if not parts or '..' in parts:
                    continue
                destination = target.joinpath(*parts)
                if item.is_dir():
                    destination.mkdir(parents=True, exist_ok=True)
                else:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(z.read(item))
                    mode = item.external_attr >> 16
                    if mode:
                        destination.chmod(mode & 0o777)
        (target / '.complete').write_text(package)
        print('Installed and verified', package, flush=True)
        return
    raise RuntimeError('No Linux archive for ' + package)

def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    repo_file = CACHE / 'repository.xml'
    fetch(BASE + 'repository2-1.xml', repo_file)
    repo = ET.parse(repo_file).getroot()
    install(repo, 'platforms;android-35', 'platform')
    install(repo, 'build-tools;35.0.0', 'build-tools')
    # Retain the exact media already approved in this conversation.
    media = ROOT / 'app/src/main/assets/media'
    asset_base = 'https://d8j0ntlcm91z4.cloudfront.net/user_3KsWlzuL984qcIlcvjWdKhGWUo3/'
    fetch(asset_base + 'hf_20261027_083603_a2a13f80-acf8-466b-9f32-04c95d2dd00d.mp4', media / 'intro.mp4')
    fetch(asset_base + 'hf_20261027_083444_d258b69a-5d6d-423f-b713-3ee5ed7e93dc.mp3', media / 'enter.mp3')
    print('Android tools and approved media ready.', flush=True)

if __name__ == '__main__':
    main()
