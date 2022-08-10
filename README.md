# Web page grabber
Web pages scrapping and parsing for data extraction for the following projects.

The project is based on [Apache AirFlow](https://github.com/apache/airflow) and 
can be deployed in [Docker](https://www.docker.com/). 

NB. The user, password and key must be specified in [`docker-compose.yml`](docker-compose.yml)
(see <REPLACE_BY_AIRFLOW_USER>, <REPLACE_BY_AIRFLOW_PASSWORD> and <REPLACE_BY_RANDOM_STRING>).

## News grabbing
 
The initialization script is [`.\db\init\utils\init_db_sources.py`](db\init\utils\init_db_sources.py).

The DAG described in [`.\dags\grab_rss.py`](dags\grab_rss.py).

The result can be accessed in Redis DB #1.


## Currency rate grabbing

The initialization isn't required.

The DAG described in [`.\dags\grab_currency_rate.py`](dags\grab_currency_rate.py).

The result can be accessed in Redis DB #2.