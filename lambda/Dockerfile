FROM public.ecr.aws/lambda/python:3.7

RUN yum update -y
RUN yum -y install gcc

WORKDIR /var/task/

COPY app/requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY ./app app

ENV PYTHONPATH="/var/task/app/"

CMD ["app/main.handler"]