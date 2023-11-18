FROM python:3.12.0

WORKDIR /app

RUN apt update \
    && apt upgrade -y \
    && pip install --upgrade pip \
    && pip install openai \
                   flask \
                   packaging
