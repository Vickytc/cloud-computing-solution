"""
Script Name: end2end.py
Description: Main test function in 3rd-iteration.
Authors:
    Qingze Wang (1528654)
    Ze Pang (955698) 
Usage:
    python3 tests/end2end.py
"""


import unittest
import requests
import json
import time
from unittest.mock import patch
from test_data import *

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
    def test_setUp(self):
        self.assertEqual(test_request.delete('/tstwipe3').status_code, 200)
        time.sleep(5)

    def test_mtd(self):
        """
        Test case for testing Mastodon methods with data.
        """
        data1, data2, data3 = TEST_MTD_LIST
        self.assertEqual(test_request.put('/tstmtd3/1', data1).status_code, 201)
        self.assertEqual(test_request.put('/tstmtd3/2', data2).status_code, 201)

        time.sleep(1)
        r = test_request.get('/tstmtd3/1')
        self.assertEqual(r.status_code, 200)
        o = r.json()['_source']
        self.assertEqual(o['content'], 'test example 1')

        r = test_request.get('/tstmtd3/2')
        self.assertEqual(r.status_code, 200)
        o = r.json()['_source']
        self.assertEqual(o['content'], 'test example 2')

        r = test_request.put('/tstmtd3/1', data3)
        self.assertEqual(r.status_code, 200)
        r = test_request.get('/tstmtd3/1')
        o = r.json()['_source']
        self.assertEqual(r.status_code, 200)
        self.assertEqual(o['content'], 'test example 3')

        self.assertEqual(test_request.get('/tstmtd3/999').status_code, 404)

        self.assertEqual(test_request.delete('/tstmtd3/1').status_code, 200)
        self.assertEqual(test_request.delete('/tstmtd3/2').status_code, 200)




    def test_mtds(self):
        """
        Test case for testing Mastodon methods without data.
        """
        data1, data2, data3 = TEST_MTD_LIST
        self.assertEqual(test_request.put('/tstmtd3/1', data1).status_code, 201)
        self.assertEqual(test_request.put('/tstmtd3/2', data2).status_code, 201)
        time.sleep(1)

        r = test_request.get('/tstmtds3')
        o = (r.json()['hits'])['hits']
        self.assertEqual(r.status_code, 200)
        self.assertEqual(o[0]['_source']['content'], "test example 1")
        self.assertEqual(o[1]['_source']['content'], "test example 2")


    def test_tw(self):
        """
        Test case for testing Twitter methods with data.
        """
        data1, data2, data3 = TEST_TW_LIST
        self.assertEqual(test_request.put('/tsttw3/1', data1).status_code, 201)
        self.assertEqual(test_request.put('/tsttw3/2', data2).status_code, 201)

        time.sleep(1)
        r = test_request.get('/tsttw3/1')
        self.assertEqual(r.status_code, 200)
        o = r.json()['_source']
        self.assertEqual(o['content'], 'test example 1')

        r = test_request.get('/tsttw3/2')
        self.assertEqual(r.status_code, 200)
        o = r.json()['_source']
        self.assertEqual(o['content'], 'test example 2')


        r = test_request.put('/tsttw3/1', data3)
        self.assertEqual(r.status_code, 200)
        r = test_request.get('/tsttw3/1')
        o = r.json()['_source']
        self.assertEqual(r.status_code, 200)
        self.assertEqual(o['content'], 'test example 3')

        self.assertEqual(test_request.get('/tsttw3/999').status_code, 404)

        self.assertEqual(test_request.delete('/tsttw3/1').status_code, 200)
        self.assertEqual(test_request.delete('/tsttw3/2').status_code, 200)

    def test_tws(self):
        """
        Test case for testing Twitter methods without data.
        """
        data1, data2, data3 = TEST_TW_LIST
        self.assertEqual(test_request.put('/tsttw3/1', data1).status_code, 201)
        self.assertEqual(test_request.put('/tsttw3/2', data2).status_code, 201)
        time.sleep(1)

        r = test_request.get('/tsttws3')
        o = (r.json()['hits'])['hits']
        self.assertEqual(r.status_code, 200)
        self.assertEqual(o[0]['_source']['content'], "test example 1")
        self.assertEqual(o[1]['_source']['content'], "test example 2")


if __name__ == '__main__':

    test_request = HTTPSession('http', 'localhost', 9090)
    unittest.main()
