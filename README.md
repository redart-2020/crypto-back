# Quick start

launch:
```shell script
docker build -t hack .
docker run --rm -ti -p 5000:5000
```

try:
```shell script
http http://localhost:5000/keys/tim
http http://localhost:5000/sign/tim file@main.py key_name=tim
```
