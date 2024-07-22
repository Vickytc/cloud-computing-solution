"""
Script Name: wipedatabase.py
Description: Wipe Elasticsearch database.
Authors:
    Qingze Wang (1528654)
    Ze Pang (955698) 
Fission Setup:
    fission function create --spec \
        --name tstwipe4 \
        --env python4 \
        --code ./functions/wipedatabase/wipedatabase.py \
        --configmap parameters4
    fission route create --spec \
        --url '/tstwipe4' \
        --function tstwipe4 \
        --name tstwipe4 \
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
    with open(f'/configs/default/parameters3/{k}', 'r', encoding='utf-8') as f:
        return f.read()

def main():
    """
    Main function to wipe and recreate Elasticsearch databases.

    Returns:
        Tuple[Dict[str, Any], int]: A tuple containing the response body (a dictionary) and the HTTP status code (an integer).
    """
    # Deleting and recreating Mastodon database
    r = requests.delete(f'{config("ES_URL")}/{config("ES_DATABASE_MTD")}',
                        verify=False,
                        auth=(config("ES_USERNAME"), config("ES_PASSWORD")))
    if r.status_code == 200:
        current_app.logger.info(f"Mastodon database wiped! {r.status_code}")
    else:
        current_app.logger.info(f"{r.status_code}, {r.text}")
    r = requests.put(f'{config("ES_URL")}/{config("ES_DATABASE_MTD")}',
                     verify=False,auth=(config("ES_USERNAME"), config("ES_PASSWORD")),
                     headers={'Content-type': 'application/json'},
                     data=config("ES_SCHEMA_MTD"))
    
    current_app.logger.info(f"{r.status_code}, {r.text}")

    # Deleting and recreating Twitter database
    r = requests.delete(f'{config("ES_URL")}/{config("ES_DATABASE_TW")}',
                        verify=False,
                        auth=(config("ES_USERNAME"), config("ES_PASSWORD")))
    if r.status_code == 200:
        current_app.logger.info(f"Twitter database wiped! {r.status_code}")
    else:
        current_app.logger.info(f"{r.status_code}, {r.text}")
    r = requests.put(f'{config("ES_URL")}/{config("ES_DATABASE_TW")}',
                     verify=False,
                     auth=(config("ES_USERNAME"), config("ES_PASSWORD")),
                     headers={'Content-type': 'application/json'},
                     data=config("ES_SCHEMA_TW"))
    current_app.logger.info(f"{r.status_code}, {r.text}")
    return r.json(), r.status_code
