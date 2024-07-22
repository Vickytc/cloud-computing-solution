"""
Script Name: twitter.py
Description: Upload either twitter file to Elasticsearch.  
Authors:
    Luxi Bai(1527822)
    Jiajun Li (1132688)
    Ze Pang (955698) 
"""

from config import *
from uploader import Uploader



if __name__=="__main__":
    uploader = Uploader("twitter-test3", buffer_size=100)
    uploader.create_index(TWITTER_SCHEMA_PATH)
    uploader.upload_jsonl(TWITTER_DATA_PATH, "topic-twitter")

