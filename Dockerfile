FROM python:3.12-alpine3.19 as app-base
LABEL maintainer="yaserkh@gmail.com"

ARG DEV=true

ENV PYTHONBUFFERED=1
ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONHASHSEED=random
ENV PIP_NO_CACHE_DIR=off
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_DEFAULT_TIMEOUT=100
ENV POETRY_VERSION=1.8.2

WORKDIR /app

COPY ./pyproject.toml /app/
COPY ./poetry.lock /app/
COPY ./app /app

RUN set -e

RUN apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev

RUN pip install "poetry==$POETRY_VERSION" && \
    poetry config virtualenvs.create false && \
    if [ $DEV = "true" ]; then \
        poetry install --no-interaction --no-root --no-ansi ; \
    else \
        poetry install --no-interaction --no-root --no-ansi --no-dev ; \
    fi

RUN rm -rf .tmp-build-deps
