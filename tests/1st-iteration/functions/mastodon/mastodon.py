"""
Script Name: mastodon.py
Description: Test the connection with fission.
Authors:
    Qingze Wang (1528654)
    Ze Pang (955698) 
Fission Setup:
    fission function create --spec \
        --name tstmtd1 \
        --env python3 \
        --code ./functions/mastodon/mastodon.py
    fission route create --spec \
        --url '/tstmtd1/{id:[0-9_]+}' \
        --function tstmtd1 \
        --name tstmtd1get \
        --method GET
    fission route create --spec \
        --url '/tstmtd1/{id:[0-9_]+}' \
        --function tstmtd1 \
        --name tstmtd1put \
        --method PUT
    fission route create --spec \
        --url '/tstmtd1/{id:[0-9_]+}' \
        --function tstmtd1 \
        --name tstmtd1del \
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
    return 'mastodon-test', 200
