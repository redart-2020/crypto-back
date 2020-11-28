FROM python:3.8-slim-buster

RUN mkdir files && mkdir -p /usr/share/man/man1
RUN pip install poetry
RUN echo deb http://ftp.ru.debian.org/debian/ buster main non-free contrib >> /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    openjdk-11-jre-headless \
    libreoffice-writer \
    ttf-mscorefonts-installer

COPY pyproject.toml poetry.lock /app/
WORKDIR /app

RUN poetry config virtualenvs.create false \
    && poetry install

COPY . /app

CMD ["gunicorn", "-b", "0.0.0.0:8000", "main:app"]
