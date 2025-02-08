FROM python:3.11-slim-bullseye

RUN apt-get update
RUN pip install icalendar pyyaml

RUN mkdir -p /var/task
WORKDIR /var/task
COPY app.py /var/task
COPY *.yaml /var/task

#ENTRYPOINT["/usr/local/bin/python"]
#CMD["--config"]
