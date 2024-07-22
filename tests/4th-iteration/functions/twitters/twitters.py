"""
Script Name: twitters.py
Description: Test Elasticsearch methods.
Authors:
    Qingze Wang (1528654)
    Ze Pang (955698) 
Fission Setup:
    fission function create --spec \
        --name tsttws4 \
        --env python3 \
        --code ./functions/twitters/twitters.py \
        --configmap parameters4
    fission route create --spec \
        --url '/tsttws4' \
        --function tsttws4 \
        --name tsttws4get \
        --method GET
"""

from flask import request, current_app
import requests, logging, json
from typing import Tuple, Union, Dict, Any


class Commons:
    @staticmethod
    def config(k: str) -> str:
        """
        Reads the configuration parameter from the specified file.

        Args:
            k (str): The key for the configuration parameter.

        Returns:
            str: The configuration value.
        """
        with open(f'/configs/default/parameters4/{k}', 'r') as f:
            return f.read()

def main():
    """
    Main function to perform a POST request to an Elasticsearch database and return the response.

    Returns:
        Tuple[Dict[str, Any], int]: A tuple containing the JSON response from the Elasticsearch query and the status code.
    """
    cm = Commons()
    try:
        # Construct the Elasticsearch search request
        r = requests.post(f'{cm.config("ES_URL")}/{cm.config("ES_DATABASE_MTD")}/_search',
                          verify=False,
                          auth=(cm.config('ES_USERNAME'), cm.config('ES_PASSWORD')),
                          headers={'Content-type': 'application/json'},
                          data=json.dumps({
                              '_source': True,
                              'query': {
                                  'match_all': {},
                              },
                              'sort': [{'created_at': {'order': 'asc'}}]
                          })
                          )
        # Return the JSON response and status code
        return r.json(), r.status_code

    except Exception as e:
        # Log the exception and return an error message with a 500 status code
        current_app.logger.error(e)
        return {'message': f'Error {e}'}, 500



