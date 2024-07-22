"""
Script Name: mastodon.py
Description: Test Elasticsearch methods
Authors:
    Qingze Wang (1528654)
    Ze Pang (955698) 
Fission Setup:
    fission function create --spec \
        --name tstmtd3 \
        --env python3 \
        --code ./functions/mastodon/mastodon.py \
        --configmap parameters3
    fission route create --spec \
        --url '/tstmtd3/{id:[0-9_]+}' \
        --function tstmtd3 \
        --name tstmtd3get \
        --method GET 
    fission route create --spec \
        --url '/tstmtd3/{id:[0-9_]+}' \
        --function tstmtd3 \
        --name tstmtd3put \
        --method PUT
    fission route create --spec \
        --url '/tstmtd3/{id:[0-9_]+}' \
        --function tstmtd3 \
        --name tstmtd3del \
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



def docurl() -> str:
    """Constructs the URL for accessing a document in Elasticsearch based on request headers.

    Returns:
        str: The constructed URL.
    """
    return f'{config("ES_URL")}/{config("ES_DATABASE_MTD")}/_doc/{request.headers["X-Fission-Params-Id"]}'


def main():
    """
    Main function to handle HTTP methods (GET, PUT, DELETE) for accessing Elasticsearch documents.

    Returns:
        Tuple[Dict[str, Any], int]: A tuple containing the response body (a dictionary) and the HTTP status code (an integer).
    """

    try:
        if request.method == 'GET':
            # Sending a GET request to retrieve the document
            r = requests.get(docurl(),
                             verify=False,
                             auth=(config("ES_USERNAME"), config("ES_PASSWORD")),
                             timeout=120)
            return r.json(), r.status_code

        elif request.method == 'PUT':
            # Sending a GET request to check if the document exists
            r = requests.get(docurl(),
                             verify=False,
                             auth=(config("ES_USERNAME"), config("ES_PASSWORD")),
                             )
            current_app.logger.info(f"{r.status_code}, {r.content}")

            if r.status_code == 200:
                # Constructing parameters for conditional update based on document version
                params={'if_seq_no': r.json()['_seq_no'], 'if_primary_term': r.json()['_primary_term']}
            else:
                params= {}
                
            # Sending a PUT request to update the document
            r = requests.put(docurl(),
                             verify=False,
                             auth=(config("ES_USERNAME"), config("ES_PASSWORD")),
                             headers={'Content-type': 'application/json'},
                             data=json.dumps(request.json),
                             params=params,
                             )
            current_app.logger.info(f"{r.status_code}, {r.content}")
            return r.json(), r.status_code

        elif request.method == 'DELETE':
            # Sending a GET request to check if the document exists
            r = requests.get(docurl(),
                             verify=False,
                             auth=(config("ES_USERNAME"), config("ES_PASSWORD")),
                             timeout=120)

            if r.status_code != 200:
                # Returning the response if the document does not exist
                return r.json(), r.status_code

            # Constructing parameters for conditional delete based on document version
            params = {'if_seq_no': r.json()['_seq_no'], 'if_primary_term': r.json()['_primary_term']}

            # Sending a DELETE request to delete the document
            r = requests.delete(docurl(),
                                verify=False, 
                                auth=(config("ES_USERNAME"), config("ES_PASSWORD")),
                                params=params,
                                timeout=120)
            current_app.logger.info(f"{r.status_code}, {r.content}")
            return r.json(), r.status_code
        
    except Exception as e:
        # Logging and returning an error response if an exception occurs
        current_app.logger.error(e)
        return {'message': f'Error {e}'}, 500
    
    # Returning a response for unsupported HTTP methods
    return {'message':'Method not allowed'}, 405

