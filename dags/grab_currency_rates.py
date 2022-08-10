#!/usr/bin/python3
# -*- coding: utf-8 -*-
import requests
import json
import datetime as dt
from bs4 import BeautifulSoup
from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
from os import getenv
from pprint import pprint
from walrus import Database

RATES_GRABBER_CONNECTION_URI = getenv('RATES_GRABBER_CONNECTION_URI', 'redis://redis:6379/2')

DEFAULT_ARGS = {
    'owner': 'airflow',
    'start_date': dt.datetime(2020, 10, 15),
    'retries': 2,
    'retry_delay': dt.timedelta(hours=1),
    'depends_on_past': False,
}

DATE_SELECTOR = '#online > div:nth-child(1) > div > p'

VALUE_SELECTORS = {
    'USD': '#online > div:nth-child(2) > div > div > div:nth-child(2) > div:nth-child(4)',
    'EUR': '#online > div:nth-child(2) > div > div > div:nth-child(3) > div:nth-child(4)',
    'GBP': '#online > div:nth-child(2) > div > div > div:nth-child(4) > div:nth-child(4)',
    'CHF': '#online > div:nth-child(2) > div > div > div:nth-child(5) > div:nth-child(4)',
    'JPY': '#online > div:nth-child(2) > div > div > div:nth-child(6) > div:nth-child(4)'
}


def grab_rates():
    db = Database().from_url(RATES_GRABBER_CONNECTION_URI)

    url = 'https://www.raiffeisen.ru/currency_rates/?active_tab=online'
    rates_page = requests.get(url)
    soup = BeautifulSoup(rates_page.content, 'html.parser')

    date_text = soup.select_one(DATE_SELECTOR).text
    date_parts = date_text.split(' ')
    rates_time = date_parts[3]
    rates_date = date_parts[5]

    for currency, selector in VALUE_SELECTORS.items():
        rate_record = {
            'date': f'{rates_date} {rates_time}',
            'rate_buy': float(soup.select_one(selector).text)
        }

        pprint(f'{currency}: {json.dumps(rate_record)}')

        rates = db.Set(currency)
        rates.add(json.dumps(rate_record))


dag = DAG(dag_id='grab_currency_rates', default_args=DEFAULT_ARGS, schedule_interval=dt.timedelta(hours=1))

grab_rates_task = PythonOperator(
        task_id='grab_rates',
        python_callable=grab_rates,
        dag=dag
)
