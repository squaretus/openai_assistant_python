FROM python:3.12.0

WORKDIR /app

RUN apt update \
    && apt upgrade -y \
    && apt install -y postgresql-client \
                   net-tools \
    && pip install --upgrade pip \
    && pip install langchain \
                   langchain_ollama \
                   langchain_core \
                   langchain_chroma \
                   langchain_community \
                   pypdf \
                   psycopg2 \
                   pandas
