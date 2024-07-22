"""
Script Name: mastodon.py
Description: Test the connection with Elasticsearch.
Authors:
    Qingze Wang (1528654)
    Ze Pang (955698) 
Fission Setup:
    fission function create --spec \
        --name tstmtd2 \
        --env python3 \
        --code ./functions/mastodon/mastodon.py \
        --configmap parameters2
    fission route create --spec \
        --url '/tstmtd2/{id:[0-9_]+}' \
        --function tstmtd2 \
        --name tstmtd2get \
        --method GET 
    fission route create --spec \
        --url '/tstmtd2/{id:[0-9_]+}' \
        --function tstmtd2 \
        --name tstmtd2put \
        --method PUT
    fission route create --spec \
        --url '/tstmtd2/{id:[0-9_]+}' \
        --function tstmtd2 \
        --name tstmtd2del \
        --method DELETE
"""


from flask import request, current_app
import requests, logging, json


def config(k: str) -> str:
    """Get the value from configmap (key-value pair) with specified key.

    Args:
        k (str): key

    Returns:
        str: value
    """
    with open(f'/configs/default/parameters2/{k}', 'r', encoding='utf-8') as f:
        return f.read()


def main():
    """
    Main function to retrieve data from an Elasticsearch database.

    Returns:
        Tuple[str, int]: A tuple containing the response body and the HTTP status code.

    """
    r = requests.get(f'{config("ES_URL")}/{config("ES_DATABASE_MTD")}',
                     auth=(config("ES_USERNAME"), config("ES_PASSWORD")),
                     verify=False,
                     timeout=120)
    
    # Extracting the index_name from the JSON response
    index_name = list(r.json().keys())[0]
    return index_name, r.status_code
