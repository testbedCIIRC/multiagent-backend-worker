import os
import time
import jinja2
import json


def generate_tasks():
    """Generates [project_folder]/tasks/__init__.py and [project_folder]/tasks/amqp_reporting.py
    based on /config.json located in the / folder.

    These files are empty until generated via this function.

    Function is blocking until /config.json appears.
    """

    config_path = '/config.json'
    if not os.path.isfile(config_path):
        print('waiting for config.json')

    while not os.path.isfile(config_path):
        time.sleep(1)

    with open(config_path) as file:
        json_dic = json.load(file)

    template = jinja2.Template("""
import subprocess
from celery import Celery
import pika
from .amqp_reporting import channel

app = Celery('{{ Celery_app_name }}', broker='{{ Celery_broker_url }}', backend='{{ Celery_backend_url }}')

app.conf.task_default_exchange = '{{ Celery_exchange }}'
app.conf.task_default_queue = '{{ worker_name }}'
app.conf.task_default_routing_key = '{{ worker_name }}'


{% for task in tasks %}

@app.task(name='{{ task.task_name }}')
def run_task():
    channel.basic_publish(exchange='{{ Reporting_exchange }}', routing_key='{{ Reporting_routing_key }}',
                          body=b'Starting {{ task.task_name }} on {{ worker_name }}')

    command = '/executables/' + '{{task.executable_path}}/' + '{{ task.command_string }}'
    proc = subprocess.run(command.split(' '))
    try:
        proc.check_returncode()
        channel.basic_publish(exchange='{{ Reporting_exchange }}', routing_key='{{ Reporting_routing_key }}',
                              body=b'Task {{ task.task_name }} on {{ worker_name }} finished')
    except subprocess.CalledProcessError as error:
        channel.basic_publish(exchange='{{ Reporting_exchange }}', routing_key='{{ Reporting_routing_key }}',
                              body=b'Task {{ task.task_name }} on {{ worker_name }} returned non-zero return code')
        pass
    except Exception as e:
        channel.basic_publish(exchange='{{ Reporting_exchange }}', routing_key='{{ Reporting_routing_key }}',
                              body=b'Task {{ task.task_name }} on {{ worker_name }} has exploded')
                          
{% endfor %}
    """)

    template_2 = jinja2.Template("""
import pika

connection_parameters = pika.ConnectionParameters('{{ Reporting_broker_url }}')
connection = pika.BlockingConnection(connection_parameters)

channel = connection.channel()
channel.exchange_declare('{{ Reporting_exchange }}', exchange_type='topic', durable=True)
        """)

    x = template.render(json_dic)

    y = template_2.render(json_dic)

    with open('tasks/__init__.py', 'w') as tasks_file:
        tasks_file.write(x)

    with open('tasks/amqp_reporting.py', 'w') as report_file:
        report_file.write(y)


if __name__ == '__main__':
    generate_tasks()
