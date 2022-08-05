# syntax=docker/dockerfile:1

FROM ubuntu:latest
RUN apt-get -y update
RUN apt-get -y install git
RUN apt-get -y install python3 python3-pip

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "./bot.py"]
