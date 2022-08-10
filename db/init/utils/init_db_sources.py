#!/usr/bin/python3
from glob import glob
from walrus import *


def init_db_sources(host='localhost', port=6379, db=1):
    with Database(host=host, port=port, db=db) as db:
        sources = db.Set('sources')
        sources.clear()
        for ds_filename in glob('./datasource/datasource.*.csv'):
            agency = ds_filename.split('.')[2]
            with open(ds_filename, mode='rt') as ds_file:
                for url in ds_file:
                    sources.add(json.dumps({'agency': agency, 'url': url[:-1]}))


if __name__ == '__main__':
    init_db_sources()
