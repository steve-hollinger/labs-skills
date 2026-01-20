# EXERCISE 1: This Dockerfile has multiple issues
# Your task: Optimize this to reduce image size by 80%+

FROM python:3.12

RUN apt-get update
RUN apt-get install -y gcc g++ make
RUN apt-get install -y curl wget vim
RUN pip install flask gunicorn requests numpy pandas

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 5000
CMD python app.py
