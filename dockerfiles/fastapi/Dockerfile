FROM python:3.8-slim

WORKDIR /app
COPY . .
COPY requirements.txt /requirements.txt

RUN apt-get update && apt-get install -y curl
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /requirements.txt
RUN pip install pydevd-pycharm~=242.23339.19

EXPOSE 8800
