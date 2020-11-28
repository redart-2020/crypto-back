from pathlib import Path

from flask import Flask, request
from werkzeug.utils import secure_filename

from core import (
    check_cert,
    check_key,
    check_file,
    convert_to_pdfa,
    sign_file,
    pack_file_with_signature,
    available_keys,
)


app = Flask(__name__)


@app.route('/sign/<username>', methods=['post'])
def sign(username):
    f = request.files.get('file')
    if not f:
        return "file required", 400

    if not check_cert(username):
        return "user has not certificate", 500
    key_pass = request.form.get('passphrase')
    key_name = request.form.get('key_name')
    if not check_key(username, key_name, key_pass):
        return "key not found", 500
    if not check_file(f):
        return "wrong file format", 400

    pdf = convert_to_pdfa(f)
    if not pdf:
        return "cant convert to pdf", 400

    signature = sign_file(username, key_name, pdf, key_pass)
    filename = Path(secure_filename(f.filename)).stem
    archive = pack_file_with_signature(pdf, signature, filename)
    return archive, [('Content-Type', 'application/zip'),
                     ('Content-Disposition', f'attachment; filename="{filename}.zip"')]


@app.route('/keys/<username>')
def keys(username):
    available = available_keys(username)
    return {'keys': available}


if __name__ == '__main__':
    app.run(host='0.0.0.0')
