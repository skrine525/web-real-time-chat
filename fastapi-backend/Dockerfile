FROM python:3.12

WORKDIR /app

ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip
COPY . .
RUN pip install poetry
RUN poetry install
