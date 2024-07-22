"""
Script Name: uploader.py
Description: Upload either jsonl file or csv file to Elasticsearch. 
Authors:
    Luxi Bai(1527822)
    Jiajun Li (1132688)
    Ze Pang (955698)  
"""

import json
import requests

import pandas as pd
from elasticsearch8 import Elasticsearch

from config import *


class Uploader:
    def __init__(self, index_name: str, buffer_size: int):
        """Initializes the Uploader class with index name and buffer size.

        Args:
            index_name (str): The Elasticsearch index name to store data.
            buffer_size (int): Size of buffer
        """
        self.index_name = index_name
        self.buffer = []
        self.buffer_size = buffer_size
        
    def create_index(self, schema_path: str) -> None:
        """Creates an Elasticsearch index using the provided schema.

        Args:
            schema_path (str): The relative path of schema json file
        """
        self.es_client = Elasticsearch (
            'https://127.0.0.1:9200',
            basic_auth=(ES_USERNAME, ES_PASSWORD),
            verify_certs= False,
            ssl_show_warn=False
        )
        # Load JSON schema from a schema_path
        with open(schema_path, 'r', encoding='utf-8') as schema_file:
            schema = json.load(schema_file)
        if not self.es_client.indices.exists(index=self.index_name):
            self.es_client.indices.create(index=self.index_name, body=schema)
            print(f"Index '{self.index_name}' created.")
        else:
            print(f"Index '{self.index_name}' already exists.")
        

    def upload_jsonl(self, data_path: str, topic_type: str) -> None:
        """Uploads JSONL data to the specified kafka topic.

        Args:
            data_path (str): The relative path of jsonl data file
            topic_type (str): The kafka topic
        """
        with open(data_path, "r", encoding='utf-8') as data_file:
            for line in data_file:
                doc = json.loads(line)
                
                if doc["lang"]=="en":
                    self.buffer.append(doc)
                if len(self.buffer) >= self.buffer_size:
                    self.flush_buffer(topic_type)
    

    def upload_csv(self, data_path: str, topic_type: str) -> None:
        """Uploads JSONL data to the specified kafka topic.

        Args:
            data_path (str): The relative path of csv data file
            topic_type (str): The kafka topic
        """
        self.buffer = pd.read_csv(data_path).to_dict(orient='records')
        self.flush_buffer(topic_type)


    def flush_buffer(self, topic_type: str):
        """Flushes the buffer by sending data to the specified topic.

        Args:
            topic_type (str): The kafka topic
        """
        requests.post(url=f'http://localhost:9090/enqueue/{topic_type}',
                      headers={'Content-Type': 'application/json'},
                      data=json.dumps({"index_name":self.index_name, "docs":self.buffer}, default=str),
                      timeout=60,
                      )
        self.buffer.clear()
