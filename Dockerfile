FROM python:3.10-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install poetry==1.6.1

COPY pyproject.toml poetry.lock  ./

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

COPY . /app/

RUN chmod +x ./entrypoint.sh
RUN chmod +x ./entrypoint_celery.sh
