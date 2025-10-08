FROM python:3.12-alpine3.22

RUN apk update && apk add \
    libpq-dev

COPY ./ /app

RUN cd /app && \
    pip install -r requirements.txt -U

WORKDIR /app