ARG FROM=pytorch/torchserve:latest-cpu
FROM ${FROM}

WORKDIR /app

COPY src/ /app

RUN pip3 install --no-cache-dir 'fast-dash' 'gunicorn'

ARG PORT=5000

CMD exec gunicorn wsgi:server --bind ":${PORT}"

EXPOSE ${PORT}
