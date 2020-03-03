FROM tensorflow/tensorflow:1.15.2-gpu-py3

RUN apt-get -y update && apt-get -y install gcc

WORKDIR /

COPY gc_req.txt /
RUN python3 -m pip --no-cache-dir install -r gc_req.txt

EXPOSE 8080

RUN mkdir checkpoint

COPY checkpoint/dnd12 /checkpoint/dnd12
COPY gpt_2_simple /gpt_2_simple
COPY docker_wrapper.sh /

COPY ecs_app.py /
COPY generate_one.py /

RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENTRYPOINT ["gunicorn", "-w", "6", "-k", "uvicorn.workers.UvicornWorker", "-t", "300", "-b", "0.0.0.0:8080", "ecs_app"]
