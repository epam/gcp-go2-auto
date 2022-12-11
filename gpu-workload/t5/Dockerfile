ARG FROM=python:3.10-alpine
FROM ${FROM}

ARG PORT=8050
ENV PORT=${PORT}

WORKDIR /app

COPY src/ /app

RUN pip3 install --no-cache-dir \
    'fast-dash' \
    'gunicorn' \
    'requests'

CMD exec gunicorn wsgi:server --bind "0.0.0.0:${PORT}"

EXPOSE ${PORT}
