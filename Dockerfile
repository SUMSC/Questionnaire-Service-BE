FROM python:3.6-slim

LABEL VERSION="1.1" MAINTAINER="Amber<wzhzzmzzy@gmail.com>"

VOLUME /var/log/eform

EXPOSE 8002

WORKDIR /opt/resource

ADD resource ./resource
ADD requirements.txt ./
ADD gunicorn.conf.py ./
ADD config.py ./

RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

ENTRYPOINT  ["gunicorn", "--config=gunicorn.conf.py", "resource:create_app()"]
