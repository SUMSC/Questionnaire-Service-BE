FROM python:3.6-slim

LABEL VERSION="1.1" MAINTAINER="Amber<wzhzzmzzy@gmail.com>"

EXPOSE 8001

VOLUME /var/log/eform

WORKDIR /opt/resource

ADD resource ./resource

ADD requirements.txt ./

ADD gunicorn.conf.py ./

RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

ENTRYPOINT  ["gunicorn", "--config=gunicorn.conf.py", "auth:create_app()"]
