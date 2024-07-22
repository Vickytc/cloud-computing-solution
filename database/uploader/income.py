"""
Script Name: income.py
Description: Upload either income file to Elasticsearch.  
Authors:
    Jiajun Li (1132688)
    Qingze Wang (1528654)
    Ze Pang (955698) 
"""

from config import *
from uploader import Uploader



if __name__=="__main__":
    uploader = Uploader("income-test3", buffer_size=100)
    uploader.create_index(INCOME_SCHEMA_PATH)
    uploader.upload_csv(INCOME_DATA_PATH, "topic-income")

