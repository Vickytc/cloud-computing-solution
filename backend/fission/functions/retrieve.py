"""
Script Name: retrieve.py
Description: Retrieve all documents from Elasticsearch.
Authors:
    Jiajun Li (1132688)
    Qingze Wang (1528654)
    Ze Pang (955698) 
Fission Setup:
    fission function create --spec \
        --name retrieve \
        --env python3 \
        --code ./functions/retrieve.py \
        --fntimeout=300 \
        --configmap configmap-es

    fission route create --spec \
        --url '/retrieve/{server:[a-zA-Z0-9_]+}' \
        --function retrieve \
        --name retrieve-get1 \
        --createingress \
        --method GET 

Example Usage:
    curl http://localhost:9090/retrieve/educ
    curl http://localhost:9090/retrieve/incomepsnl
"""

import json

from typing import Tuple, Generator, Any

from flask import current_app, request
from elasticsearch8 import Elasticsearch, helpers


def config(k: str) -> str:
    """Get the value from configmap (key-value pair) with specified key.

    Args:
        k (str): key

    Returns:
        str: value
    """
    with open(f'/configs/default/configmap-es/{k}', 'r', encoding='utf-8') as f:
        return f.read()


def main() -> Tuple[str, int]:
    def retrieve_all_docs(es: Elasticsearch, index_name: str) -> Generator[Any, None, None]:
        """Retrieve all documents from the specified Elasticsearch index.

        Args:
            es (Elasticsearch): The Elasticsearch client instance.
            index_name (str): The name of the index to retrieve documents from.

        Yields:
            dict: The source of each document.
        """
        for doc in helpers.scan(es, index=index_name):
            yield doc['_source']
    try:
        # parse the server parameter, can only be any index_name in Elasticsearch
        index_name = request.headers['X-Fission-Params-Server']
        current_app.logger.info(f"index_name is {index_name}")

        # create an Elasticsearch client instance, authentication credentials from configmap
        es_client = Elasticsearch (
            'https://elasticsearch-master.elastic.svc.cluster.local:9200',
            basic_auth=(config('ES_USERNAME'), config('ES_PASSWORD')),
            verify_certs= False,
            ssl_show_warn=False,
            request_timeout=300
        )
        current_app.logger.info("start searching...")
        retrieved = list(retrieve_all_docs(es_client, index_name))
        current_app.logger.info("search finished!")
        return json.dumps(retrieved), 200
    except Exception as e:
        current_app.logger.info(str(e))
        return {'message': f'Error {e}'}, 500
