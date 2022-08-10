#!/usr/bin/python3
# -*- coding: utf-8 -*-
import requests
import json
import datetime as dt
from os import getenv
from pprint import pprint
from walrus import Database

from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator


NEWS_GRABBER_CONNECTION_URI = getenv('NEWS_GRABBER_CONNECTION_URI', 'redis://redis:6379/1')

default_args = {
    'owner': 'airflow',
    'start_date': dt.datetime(2020, 9, 8),
    'retries': 10,
    'retry_delay': dt.timedelta(minutes=1),
    'depends_on_past': False,
}


def start_grab_news():
    db = Database().from_url(NEWS_GRABBER_CONNECTION_URI)
    pprint(f'Connection URI = {NEWS_GRABBER_CONNECTION_URI}')
    result = db.Set('sources').unionstore('queue_rss_load_tasks')
    return str(result)


def grab_rss():
    db = Database().from_url(NEWS_GRABBER_CONNECTION_URI)
    pprint(f'Connection URI = {NEWS_GRABBER_CONNECTION_URI}')
    queue_rss_load_tasks = db.Set('queue_rss_load_tasks')
    queue_rss_parse_tasks = db.Set('queue_rss_parse_tasks')

    rss_load_task = queue_rss_load_tasks.pop()
    i = 0
    while rss_load_task:
        rss = json.loads(rss_load_task)
        agency = rss['agency']
        url = rss['url']
        pprint(f'Loading from <{agency}>: <{url}>')
        response = requests.get(url)
        pprint(f'Loaded from <{agency}>: <{url}> with code {response.status_code}')
        response_hash = hash(response.text)
        pprint(f'Response hash: {response_hash}')
        queue_rss_parse_tasks.add(json.dumps({'agency': agency, 'url': url, 'rss': response.text}))
        rss_load_task = queue_rss_load_tasks.pop()
        i += 1
    return f'Loaded {i} sources'


def parse_rss():
    db = Database().from_url(NEWS_GRABBER_CONNECTION_URI)
    pprint(f'Connection URI = {NEWS_GRABBER_CONNECTION_URI}')
    queue_rss_parse_tasks = db.Set('queue_rss_parse_tasks')
    queue_rss_parse_task = queue_rss_parse_tasks.pop()
    while queue_rss_parse_task:
        queue_rss_parse_task = queue_rss_parse_tasks.pop()


dag = DAG(dag_id='grab_news', default_args=default_args, schedule_interval=dt.timedelta(minutes=5))


start_grab_news_task = PythonOperator(
        task_id='start_grab_rss',
        python_callable=start_grab_news,
        dag=dag
)

for i in range(5):
    grab_rss_task = PythonOperator(
            task_id=f'grab_rss_{i}',
            python_callable=grab_rss,
            dag=dag
    )
    parse_rss_task = PythonOperator(
            task_id=f'parse_rss_{i}',
            python_callable=parse_rss,
            dag=dag
    )

    start_grab_news_task >> grab_rss_task >> parse_rss_task
