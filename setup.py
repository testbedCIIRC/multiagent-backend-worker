#!/usr/bin/env python

from distutils.core import setup

setup(name='multiagent-ordering-system-backend-worker',
      version='1.0',
      description='Docker worker contaner for multiagent system at CIIRC',
      entry_points={
          'console_scripts': [
              'prepare_config=tasks.prepare_tasks:generate_tasks'
          ],
      },
      install_requires=[
          'celery',
          'jinja2',
          'kombu',
          'pika'
          ]
      )
