"""
Script Name: end2end.py
Description: Main test function in 2nd-iteration.
Authors:
    Qingze Wang (1528654)
    Ze Pang (955698) 
Usage:
    python3 tests/end2end.py
"""


import unittest
import requests
from unittest.mock import patch

class HTTPSession:
    def __init__(self, protocol, hostname, port):
        """Initializes an HTTP session with the given protocol, hostname, and port.

        Args:
            protocol (str): The protocol (e.g., 'http' or 'https').
            hostname (str): The hostname or IP address of the server.
            port (int): The port number on which the server is running.
        """
        self.session = requests.Session()
        self.base_url = f'{protocol}://{hostname}:{port}'

    def get(self, path):
        """Sends a GET request to the specified path.

        Args:
            path (str): The path to append to the base URL.

        Returns:
            requests.Response: The response object.
        """
        return self.session.get(f'{self.base_url}/{path}')

    def post(self, path, data):
        """Sends a POST request to the specified path with the given data.

        Args:
            path (str): The path to append to the base URL.
            data (Dict): The data to send in the request body.

        Returns:
            requests.Response: The response object.
        """
        return self.session.post(f'{self.base_url}/{path}', data)

    def put(self, path, data):
        """Sends a PUT request to the specified path with the given data.

        Args:
            path (str): The path to append to the base URL.
            data (Dict): The data to send in the request body.

        Returns:
            requests.Response: The response object.
        """
        return self.session.put(f'{self.base_url}/{path}', data)

    def delete(self, path):
        """Sends a DELETE request to the specified path.

        Args:
            path (str): The path to append to the base URL.

        Returns:
            requests.Response: The response object.
        """
        return self.session.delete(f'{self.base_url}/{path}')

class TestEnd2End(unittest.TestCase):
    def test_mtd(self):
        """
        Test case for testing Mastodon methods with data.
        """
        self.assertEqual(test_request.get('/tstmtd2/111').status_code, 200)
        self.assertEqual(test_request.get('/tstmtd2/111').text, 'mastodon-test')

        self.assertEqual(test_request.put('/tstmtd2/111', {}).status_code, 200)
        self.assertEqual(test_request.put('/tstmtd2/111', {}).text, 'mastodon-test')

        self.assertEqual(test_request.delete('/tstmtd2/111').status_code, 200)
        self.assertEqual(test_request.delete('/tstmtd2/111').text, 'mastodon-test')

    def test_mtds(self):
        """
        Test case for testing Mastodon methods without data.
        """
        self.assertEqual(test_request.get('/tstmtds2').status_code, 200)
        self.assertEqual(test_request.get('/tstmtds2').text, 'mastodon-test')

    def test_tw(self):
        """
        Test case for testing Twitter methods with data.
        """
        self.assertEqual(test_request.get('/tsttw2/111').status_code, 200)
        self.assertEqual(test_request.get('/tsttw2/111').text, 'twitter-test')

        self.assertEqual(test_request.put('/tsttw2/111', {}).status_code, 200)
        self.assertEqual(test_request.put('/tsttw2/111', {}).text, 'twitter-test')

        self.assertEqual(test_request.delete('/tsttw2/111').status_code, 200)
        self.assertEqual(test_request.delete('/tsttw2/111').text, 'twitter-test')

    def test_tws(self):
        """
        Test case for testing Twitter methods without data.
        """
        self.assertEqual(test_request.get('/tsttws2').status_code, 200)
        self.assertEqual(test_request.get('/tsttws2').text, 'twitter-test')


if __name__ == '__main__':

    test_request = HTTPSession('http', 'localhost', 9090)
    unittest.main()
