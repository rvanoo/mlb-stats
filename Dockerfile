FROM python:3.6-alpine

ENV FLASK_APP app.py
ENV PYTHONUNBUFFERED 1

RUN mkdir /app
WORKDIR /app

RUN apk add --no-cache --update --virtual .build-deps build-base

ADD requirements.txt /app/
RUN pip install -r requirements.txt

RUN apk del .build-deps

ADD . /app/
