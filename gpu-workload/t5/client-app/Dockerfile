ARG BASE_IMAGE=python:3.10-alpine
FROM ${BASE_IMAGE}

ARG PORT=8050
ENV PORT=${PORT}

WORKDIR /app

COPY requirements.txt /app
COPY src/ /app

RUN pip3 install --no-cache-dir -r requirements.txt

CMD exec gunicorn wsgi:server --bind "0.0.0.0:${PORT}"

EXPOSE ${PORT}
