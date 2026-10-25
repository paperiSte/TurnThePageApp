"""Install Partitura's default soundfont over HTTPS (its fallback uses FTP)."""
import hashlib
import importlib.util
from pathlib import Path
import urllib.request

URL = 'https://ftp.osuosl.org/pub/musescore/soundfont/MuseScore_General/MuseScore_General.sf3'
SHA256 = '5b85b6c2c61d10b2b91cddd41efcce7b25cd31c8271d511c73afafbef20b6fa3'


def main():
    spec = importlib.util.find_spec('partitura')
    if spec is None:
        raise SystemExit('Install requirements.txt first.')
    target = Path(spec.origin).parent / 'assets' / 'MuseScore_General.sf3'
    if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() == SHA256:
        print('Soundfont is ready.')
        return
    # Download to a temporary sibling so interrupted downloads cannot look ready.
    temporary = target.with_suffix('.download')
    try:
        with urllib.request.urlopen(URL, timeout=60) as source, temporary.open('wb') as dest:
            while chunk := source.read(1024 * 1024):
                dest.write(chunk)
        if hashlib.sha256(temporary.read_bytes()).hexdigest() != SHA256:
            raise ValueError('Soundfont checksum differs; refusing to install it.')
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)
    print('Soundfont is ready.')

if __name__ == '__main__':
    main()
