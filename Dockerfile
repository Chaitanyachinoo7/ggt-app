FROM tiangolo/uvicorn-gunicorn:python3.8-slim

ENV TIMEOUT=600
ENV LOG_LEVEL=debug

RUN apt-get update
RUN apt-get -y install gcc
RUN pip install pipenv
COPY ./app/requirements.txt /app/
RUN pipenv lock --requirements
RUN pipenv lock --requirements > requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app /app

