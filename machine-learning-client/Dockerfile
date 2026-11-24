FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN pip install pipenv

COPY Pipfile Pipfile.lock ./

RUN pipenv install --system --deploy

COPY client ./client

EXPOSE 8000

STOPSIGNAL SIGINT

CMD ["flask", "--app", "client", "run", "--host", "0.0.0.0", "--port", "8000"]
