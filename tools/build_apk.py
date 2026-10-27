"""Build and sign a real APK using Android build tools and the installed Java compiler."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / 'tools/cache'
BUILD = ROOT / 'app/build/manual'
TOOLS = CACHE / 'build-tools'
ANDROID = CACHE / 'platform/android.jar'

def run(*args):
    result = subprocess.run([str(a) for a in args], cwd=ROOT, capture_output=True, text=True)
    if result.stdout.strip(): print(result.stdout.strip())
    if result.stderr.strip(): print(result.stderr.strip())
    result.check_returncode()
    return result.stdout

def main():
    for file in [ANDROID, TOOLS / 'aapt2', TOOLS / 'lib/d8.jar', TOOLS / 'lib/apksigner.jar']:
        if not file.is_file():
            raise SystemExit('Missing Android tools. First run: python tools/bootstrap_android.py')
    for media in ['opening.jpg', 'lobby.jpg', 'map.jpg', 'intro.mp4', 'click.wav', 'back.wav', 'confirm.wav', 'enter.mp3']:
        if not (ROOT / 'app/src/main/assets/media' / media).is_file():
            raise SystemExit('Missing required media: ' + media)
    for d in [BUILD, BUILD / 'classes', BUILD / 'dex', ROOT / 'dist']:
        d.mkdir(parents=True, exist_ok=True)
    manifest = BUILD / 'AndroidManifest.xml'
    manifest.write_text((ROOT / 'app/src/main/AndroidManifest.xml').read_text().replace(
        '<manifest xmlns:', '<manifest package="com.roguebloodmoon.prototype" xmlns:', 1))
    run(TOOLS / 'aapt2', 'compile', '--dir', ROOT / 'app/src/main/res', '-o', BUILD / 'resources.zip')
    run(TOOLS / 'aapt2', 'link', '-o', BUILD / 'base.apk', '-I', ANDROID,
        '--manifest', manifest,
        '--min-sdk-version', '26', '--target-sdk-version', '35',
        '--version-code', '2', '--version-name', '0.1.1',
        '-A', ROOT / 'app/src/main/assets', BUILD / 'resources.zip')
    sources = list((ROOT / 'app/src/main/java').rglob('*.java'))
    run('java', '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-source', '17', '-target', '17', '-encoding', 'UTF-8',
        '-classpath', ANDROID, '-d', BUILD / 'classes', *sources)
    classes = BUILD / 'classes.jar'
    with zipfile.ZipFile(classes, 'w') as z:
        for file in (BUILD / 'classes').rglob('*.class'):
            z.write(file, file.relative_to(BUILD / 'classes'))
    run('java', '-cp', TOOLS / 'lib/d8.jar', 'com.android.tools.r8.D8',
        '--lib', ANDROID, '--min-api', '26', '--output', BUILD / 'dex', classes)
    unsigned = BUILD / 'unsigned.apk'
    shutil.copyfile(BUILD / 'base.apk', unsigned)
    with zipfile.ZipFile(unsigned, 'a') as z:
        for file in (BUILD / 'dex').glob('*.dex'):
            z.write(file, file.name, compress_type=zipfile.ZIP_STORED)
    aligned = BUILD / 'aligned.apk'
    run(TOOLS / 'zipalign', '-f', '-p', '4', unsigned, aligned)
    key = ROOT.parent / '.rogue-prototype-debug.keystore'
    if not key.exists():
        run('keytool', '-genkeypair', '-keystore', key, '-storepass', 'android', '-keypass', 'android',
            '-alias', 'androiddebugkey', '-keyalg', 'RSA', '-keysize', '2048', '-validity', '10000',
            '-dname', 'CN=Rogue Prototype,O=Local Development,C=TR')
        key.chmod(0o600)
    apk = ROOT / 'dist/Rogue-Blood-Moon-v0.1.1-debug.apk'
    run('java', '-jar', TOOLS / 'lib/apksigner.jar', 'sign', '--ks', key,
        '--ks-pass', 'pass:android', '--key-pass', 'pass:android', '--ks-key-alias', 'androiddebugkey',
        '--out', apk, aligned)
    verify = run('java', '-jar', TOOLS / 'lib/apksigner.jar', 'verify', '--verbose', '--print-certs', apk)
    (ROOT / 'dist/signature-verification.txt').write_text(verify)
    badging = run(TOOLS / 'aapt', 'dump', 'badging', apk)
    (ROOT / 'dist/apk-badging.txt').write_text(badging)
    with zipfile.ZipFile(apk) as z:
        assert z.testzip() is None
        assert {'classes.dex', 'AndroidManifest.xml', 'assets/index.html', 'assets/media/intro.mp4'} <= set(z.namelist())
    report = {'apk': apk.name, 'size_bytes': apk.stat().st_size, 'sha256': hashlib.sha256(apk.read_bytes()).hexdigest(),
              'package': 'com.roguebloodmoon.prototype', 'version': '0.1.1', 'min_android': '8.0',
              'signed': True, 'device_tested': False, 'scope': 'Offline menu, intro and map concept preview'}
    (ROOT / 'dist/build-report.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
