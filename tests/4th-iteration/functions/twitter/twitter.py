"""
Script Name: twitter.py
Description: Test Elasticsearch methods.
Authors:
    Qingze Wang (1528654)
    Ze Pang (955698) 
Fission Setup:
    fission function create --spec \
        --name tsttw4 \
        --env python3 \
        --code ./functions/twitter/twitter.py \
        --configmap parameters4

    fission route create --spec \
        --url '/tsttw4/{id:[0-9_]+}' \
        --function tsttw4 \
        --name tsttw4get \
        --method GET 
    fission route create --spec \
        --url '/tsttw4/{id:[0-9_]+}' \
        --function tsttw4 \
        --name tsttw4put \
        --method PUT
    fission route create --spec \
        --url '/tsttw4/{id:[0-9_]+}' \
        --function tsttw4 \
        --name tsttw4del \
        --method DELETE
"""

from flask import request, current_app
import requests, logging, json
from typing import Tuple, Union, Dict, Any


class Commons:
    @staticmethod
    def config(k:str) -> str:
        """
        Reads the configuration parameter from the specified file.

        Args:
            k (str): The key for the configuration parameter.

        Returns:
            str: The configuration value.
        """
        with open(f'/configs/default/parameters4/{k}', 'r') as f:
            return f.read()

    @staticmethod
    def auth() -> Tuple[str, str]:
        """
        Retrieves the Elasticsearch authentication credentials.

        Returns:
            Tuple[str, str]: A tuple containing the Elasticsearch username and password.
        """
        return Commons.config("ES_USERNAME"), Commons.config("ES_PASSWORD")

    @staticmethod
    def search_url(db: str) -> str:
        """
        Constructs the search URL for the specified database.

        Args:
            db (str): The database name.

        Returns:
            str: The Elasticsearch search URL.
        """
        return f'{Commons.config("ES_URL")}/{Commons.config(db)}/_search'



class ESDocument:
    def __init__(self, commons: Commons, req: Any, db: str):
        """
        Initializes the ESDocument with the given commons, request, and database name.

        Args:
            commons (Commons): The commons instance for configuration and authentication.
            req (Any): The request object.
            db (str): The database name.
        """
        self.commons = commons
        self.req = req
        self.db = db

    def url(self) -> str:
        """
        Constructs the URL for the specific document in the database.

        Returns:
            str: The Elasticsearch document URL.
        """
        return f'{self.commons.config("ES_URL")}/{self.commons.config(self.db)}/_doc/{self.req.headers[f"X-Fission-Params-Id"]}'

    def get(self) -> Tuple[dict, int]:
        """
        Retrieves the document from Elasticsearch.

        Returns:
            Tuple[dict, int]: The document as a JSON dictionary and the HTTP status code.
        """
        r = requests.get(self.url(), verify=False, auth=self.commons.auth())
        return r.json(), r.status_code

    def put(self) -> Tuple[dict, int]:
        """
        Updates or creates the document in Elasticsearch.

        Returns:
            Tuple[dict, int]: The response as a JSON dictionary and the HTTP status code.
        """
        r = requests.get(self.url(), verify=False, auth=self.commons.auth())

        if r.status_code == 200:
            params = {'if_seq_no': r.json()['_seq_no'], 'if_primary_term': r.json()['_primary_term']}
        else:
            params = {}

        r = requests.put(self.url(), verify=False, auth=self.commons.auth(),
                         headers={'Content-type': 'application/json'},
                         data=json.dumps(request.json),
                         params=params)
        return r.json(), r.status_code

    def delete(self) -> Tuple[dict, int]:
        """
        Deletes the document from Elasticsearch.

        Returns:
            Tuple[dict, int]: The response as a JSON dictionary and the HTTP status code.
        """
        r = requests.get(self.url(), verify=False, auth=self.commons.auth())

        if r.status_code != 200:
            return r.json(), r.status_code

        r = requests.delete(self.url(), verify=False, auth=self.commons.auth(),
                            params={'if_seq_no': r.json()['_seq_no'], 'if_primary_term': r.json()['_primary_term']})
        return r.json(), r.status_code

    def all(self) -> str:
        """
        Constructs a query to retrieve all documents from the database, sorted by creation date in ascending order.

        Returns:
            str: The query as a JSON string.
        """
        return json.dumps(
            {
                '_source': True,
                'query': {
                    'match_all': {},
                },
                'sort': [
                    {
                        'created_at':
                            {
                                'order':
                                    'asc'
                            }
                    }
                ]
            }
        )


class ESTW(ESDocument):
    """
    Initializes the ESMTD with the given commons and request.

    Args:
        commons (Commons): The commons instance for configuration and authentication.
        req (Any): The request object.
    """
    def __init__(self, commons: Commons, req: Any):
        super(ESTW, self).__init__(commons, req, 'ES_DATABASE_TW')



def main() -> Tuple[Dict[str, Any], int]:
    """
    Main function to handle GET, PUT, and DELETE requests to an Elasticsearch endpoint.
    
    Returns:
        A tuple containing the response JSON and status code.
    """

    # Initialize the Commons class instance
    cm = Commons()  
    # Initialize the ESTW class instance with the commons and request
    es = ESTW(cm, request) 
    
    try:
        if request.method == 'GET':
            # Handle GET request to the Elasticsearch URL
            r = requests.get(es.url(), 
                             verify=False, 
                             auth=(cm.config("ES_USERNAME"), cm.config("ES_PASSWORD")))
            return r.json(), r.status_code

        elif request.method == 'PUT':
            # Handle PUT request to the Elasticsearch URL
            r = requests.get(es.url(), 
                             verify=False, 
                             auth=(cm.config("ES_USERNAME"), cm.config("ES_PASSWORD")))

            if r.status_code == 200:
                # If document exists, get the sequence number and primary term for optimistic concurrency control
                params = {'if_seq_no': r.json()['_seq_no'], 'if_primary_term': r.json()['_primary_term']}
            else:
                params = {}

            # Update the document with the provided JSON data
            r = requests.put(es.url(), 
                             verify=False, 
                             auth=(cm.config("ES_USERNAME"), cm.config("ES_PASSWORD")),
                             headers={'Content-type': 'application/json'},
                             data=json.dumps(request.json),
                             params=params)
            return r.json(), r.status_code

        elif request.method == 'DELETE':
            # Handle DELETE request to the Elasticsearch URL
            r = requests.get(es.url(), 
                             verify=False, 
                             auth=(cm.config("ES_USERNAME"), cm.config("ES_PASSWORD")))

            if r.status_code != 200:
                return r.json(), r.status_code

            # Delete the document with the provided sequence number and primary term
            r = requests.delete(es.url(), 
                                verify=False, 
                                auth=(cm.config("ES_USERNAME"), cm.config("ES_PASSWORD")),
                                params={'if_seq_no': r.json()['_seq_no'], 
                                        'if_primary_term': r.json()['_primary_term']})
            return r.json(), r.status_code

    except Exception as e:
        # Log any exceptions that occur and return a 500 error response
        current_app.logger.error(e)
        return {'message': f'Error {e}'}, 500

    # Return a 405 error response if the request method is not allowed
    return {'message': 'Method not allowed'}, 405
