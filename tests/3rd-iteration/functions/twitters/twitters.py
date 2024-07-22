"""
Script Name: twitters.py
Description: Test Elasticsearch methods.
Authors:
    Qingze Wang (1528654)
    Ze Pang (955698) 
Fission Setup:
    fission function create --spec \
        --name tsttws3 \
        --env python3 \
        --code ./functions/twitters/twitters.py \
        --configmap parameters3
    fission route create --spec \
        --url '/tsttws3' \
        --function tsttws3 \
        --name tsttws3 \
        --method GET 
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
    Main function to perform a search query in Elasticsearch.

    Returns:
        Tuple[Dict[str, Any], int]: A tuple containing the response body (a dictionary) and the HTTP status code (an integer).
    """

    try:
        # Sending a POST request to perform a search query
        r = requests.post(f'{config("ES_URL")}/{config("ES_DATABASE_TW")}/_search',
                verify=False,
                auth=(config('ES_USERNAME'), config('ES_PASSWORD')),
                headers={'Content-type': 'application/json'},
                data=json.dumps({
                '_source': True,
                'query': {
                    'match_all': {},
                    },
                'sort': [{'created_at': {'order': 'asc'}}]
                }),
                timeout=120
            )
        
        # Returning the JSON response and the HTTP status code
        return r.json(), r.status_code
    except Exception as e:
        # Logging and returning an error response if an exception occurs
        current_app.logger.error(e)
        return {'message': f'Error {e}'}, 500
    
