FROM ubuntu

RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y python3
RUN apt-get install -y pip
RUN pip install celery && \
    pip install redis

RUN mkdir -p /executables
WORKDIR /app

COPY tasks tasks
COPY setup.py .

RUN pip install .

CMD python3 tasks/prepare_tasks.py && \
    celery -A tasks worker -E -l INFO -n $WORKER_NAME
