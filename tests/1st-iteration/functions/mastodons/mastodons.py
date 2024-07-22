"""
Script Name: mastodons.py
Description: Test the connection with fission.
Authors:
    Qingze Wang (1528654)
    Ze Pang (955698) 
Fission Setup:
    fission function create --spec \
        --name tstmtds1 \
        --env python3 \
        --code ./functions/mastodons/mastodons.py
    fission route create --spec \
        --url '/tstmtds1' \
        --function tstmtds1 \
        --name tstmtds1 \
        --method GET 
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
