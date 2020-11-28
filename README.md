# Quick start

## launch
a) docker:
```shell script
docker build -t hack .
docker run --rm -ti -p 8000:8000 hack
```
b) local:
```
pip3 install poetry
poetry install
poetry run gunicorn main:app
```

## try
```shell script
http http://localhost:8000/sign/tim file@document.docx
```
