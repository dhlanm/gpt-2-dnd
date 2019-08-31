FROM tiangolo/uwsgi-nginx:python3.6
COPY ./* .
ADD build . 
EXPOSE 5000


https://github.com/tiangolo/uwsgi-nginx-flask-docker/blob/master/python3.6/Dockerfile copy this shit but make appropriate when less not funcitoning
