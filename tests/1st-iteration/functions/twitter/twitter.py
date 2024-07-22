"""
Script Name: twitter.py
Description: Test the connection with fission.
Authors:
    Qingze Wang (1528654)
    Ze Pang (955698) 
Fission Setup:
    fission function create --spec \
        --name tsttw1 \
        --env python3 \
        --code ./functions/twitter/twitter.py
    fission route create --spec \
        --url '/tsttw1/{id:[0-9_]+}' \
        --function tsttw1 \
        --name tsttw1get \
        --method GET 
    fission route create --spec \
        --url '/tsttw1/{id:[0-9_]+}' \
        --function tsttw1 \
        --name tsttw1put \
        --method PUT
    fission route create --spec \
        --url '/tsttw1/{id:[0-9_]+}' \
        --function tsttw1 \
        --name tsttw1del \
        --method DELETE
"""


from flask import request, current_app


def main():
    """Main function handling the incoming request.

    Returns:
        Tuple[str, int]: A tuple containing the response body and the HTTP status code.
    """
    current_app.logger.debug(f'Received request: {request.method}')

    # Returning a simple response with a string and HTTP status code
    return 'twitter-test', 200
