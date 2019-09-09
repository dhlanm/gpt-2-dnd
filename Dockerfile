FROM python:3.7.3-slim-stretch

RUN apt-get -y update && apt-get -y install gcc

WORKDIR /

RUN mkdir checkpoint

COPY checkpoint/dnd12 /checkpoint/dnd12
COPY gpt_2_simple /gpt_2_simple
COPY requirements.txt /

RUN pip3 --no-cache-dir install -r requirements.txt

COPY gcloud_app.py /

RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENTRYPOINT ["python3", "-X", "utf8", "app.py"]
