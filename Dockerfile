FROM python:3.12

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .

RUN apt-get update
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd -ms /bin/bash django_user
USER django_user

COPY . /app