import datetime
from os import listdir
from pathlib import Path
from subprocess import Popen, PIPE
from tempfile import NamedTemporaryFile
from typing import Optional, List
from zipfile import ZipFile

from OpenSSL.crypto import load_certificate, load_privatekey, sign, verify as _verify, FILETYPE_PEM, Error

# генерация ключа - openssl genrsa -out keys/tim/tim.priv 1024
#  openssl rsa -in keys/tim/tim.priv -pubout > keys/tim/tim.pub
# генерация серта - openssl req -x509 -sha256 -nodes -newkey rsa:4096 -key key -days 30 -out keys/tim/tim.crt
# подпись файла openssl dgst -sha256 -sign keys/tim/tim.priv main.py

KEY_PATH = Path('keys')
FILES_PATH = Path('files')


def available_keys(username: str) -> List[str]:
    path = KEY_PATH / username
    return list({Path(fn).stem for fn in listdir(path)})


def check_cert(username: str) -> bool:
    path = KEY_PATH / username / f'{username}.crt'
    try:
        with path.open('rb') as f:
            load_certificate(FILETYPE_PEM, f.read())
    except Exception:
        return False
    return True


def check_key(username: str, key_name: str, passphrase: Optional[str] = None) -> bool:
    path = KEY_PATH / username / f'{key_name}.priv'
    try:
        with path.open('rb') as f:
            load_privatekey(FILETYPE_PEM, f.read(), passphrase=passphrase)
    except Exception:
        return False
    return True


def check_file(fileobj) -> bool:
    return True


def convert_to_pdfa(fileobj) -> bytes:
    return fileobj.read()
    suffix = Path(fileobj.filename).suffix
    with NamedTemporaryFile(prefix=suffix) as temp:
        fileobj.save(temp)
        p = Popen(['libreoffice', '--headless', '--convert-to', 'pdf', temp.name], stdout=PIPE)
        out, err = p.communicate()
        return out


def sign_file(username: str, key_name: str, data: bytes, passphrase: Optional[str] = None,
              digest: str = 'sha256') -> bytes:
    path_to_key = KEY_PATH / username / f'{key_name}.priv'
    with path_to_key.open('rb') as f:
        private_key = load_privatekey(FILETYPE_PEM, f.read(), passphrase=passphrase)
    signature = sign(private_key, data, digest=digest)
    return signature


def pack_file_with_signature(data: bytes, signature: bytes, filename: str) -> bytes:
    timestamp = datetime.datetime.now().timestamp()
    zip_filename = FILES_PATH / f'{filename}_{timestamp}.zip'
    with ZipFile(zip_filename, 'w') as z:
        z.writestr(filename + '.pdf', data)
        z.writestr(filename + '.pdf.sig', signature)
    with open(zip_filename, 'rb') as f:
        return f.read()


def verify(data: bytes, signature: bytes, cert_filename: str, digest: str = 'sha256') -> bool:
    with open(cert_filename, 'rb') as f:
        cert = load_certificate(FILETYPE_PEM, f.read())
    try:
        _verify(cert, signature, data, digest=digest)
        return True
    except Error:
        return False
