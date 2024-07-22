"""
Script Name: twitters.py
Description: Test the connection with fission.
Authors:
    Qingze Wang (1528654)
    Ze Pang (955698) 
Fission Setup:
    fission function create --spec \
        --name tsttws1 \
        --env python3 \
        --code ./functions/twitters/twitters.py
    fission route create --spec \
        --url '/tsttws1' \
        --function tsttws1 \
        --name tsttws1 \
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
    return 'twitter-test', 200
