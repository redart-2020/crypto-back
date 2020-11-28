FROM python:3.8-slim

RUN pip install poetry

COPY pyproject.toml poetry.lock /app/
WORKDIR /app

RUN poetry config virtualenvs.create false \
    && poetry install

COPY . /app
RUN mkdir files

CMD ["python", "main.py"]
