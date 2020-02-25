# FROM nikolaik/python-nodejs:python3.6-nodejs12
# FROM python:3.7.3-slim-stretch
# FROM tiangolo/uwsgi-nginx-flask:python3.6
# FROM tiangolo/uvicorn-gunicorn-starlette:python3.6
FROM tensorflow/tensorflow::1.15.2-gpu-py3

RUN apt-get -y update && apt-get -y install gcc

WORKDIR /

COPY gc_req.txt /
RUN python3 -m pip --no-cache-dir install -r gc_req.txt

EXPOSE 8080

# RUN npm i -g pm2

RUN mkdir checkpoint

COPY checkpoint/dnd12 /checkpoint/dnd12
COPY gpt_2_simple /gpt_2_simple
# COPY build /build
COPY docker_wrapper.sh /

COPY gcloud_app.py /
# COPY front.py /app/main.py
COPY generate_one.py /

RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# CMD ./docker_wrapper.sh

# RUN python3 -X utf8 gcloud_app.py

# CMD [ "pm2", "serve", "build", "--spa" ]

ENTRYPOINT ["python3", "-X", "utf8", "gcloud_app.py"]
