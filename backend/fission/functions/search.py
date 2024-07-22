"""
Script Name: search.py
Description: Search the documents from Elasticsearch if "content" contains given "keyword".
Authors:
    Jiajun Li (1132688)
    Qingze Wang (1528654)
    Ze Pang (955698) 
Fission Setup:
    fission function create --spec \
        --name search \
        --env python3 \
        --code ./functions/search.py \
        --fntimeout=300 \
        --configmap configmap-es

    fission route create --spec \
        --url '/search/{server:[a-zA-Z0-9]+}/keyword/{keyword:[a-zA-Z0-9]+}' \
        --function search \
        --name search-get1 \
        --createingress \
        --method GET 

    fission route create --spec \
        --url '/search/{server:[a-zA-Z0-9]+}/keyword/{keyword:[a-zA-Z0-9]+}/size/{size:[0-9]+}' \
        --function search \
        --name search-get2 \
        --createingress \
        --method GET 

    fission route create --spec \
        --url '/search/{server:[a-zA-Z0-9]+}/keyword/{keyword:[a-zA-Z0-9]+}/start/{start:[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]}/end/{end:[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]}' \
        --function search \
        --name search-get3 \
        --createingress \
        --method GET 
        
    fission route create --spec \
        --url '/search/{server:[a-zA-Z0-9]+}/keyword/{keyword:[a-zA-Z0-9]+}/start/{start:[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]}/end/{end:[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]}/size/{size:[0-9]+}' \
        --function search \
        --name search-get4 \
        --createingress 
        --method GET

Example Usage:
    curl http://localhost:9090/search/twitter/keyword/ai
    curl http://localhost:9090/search/twitter/keyword/ai/size/10
    curl http://localhost:9090/search/twitter/keyword/ai/start/2022-04-18/end/2022-04-20
    curl http://localhost:9090/search/twitter/keyword/ai/start/2022-04-18/end/2022-04-20/size/10
"""

import json

from typing import Tuple

from collections import defaultdict
from flask import current_app, request
from elasticsearch8 import Elasticsearch, helpers


def config(k: str) -> str:
    """Get the value from configmap (key-value pair) with specified key.

    Args:
        k (str): key

    Returns:
        str: value
    """
    with open(f'/configs/default/configmap-es/{k}', 'r', encoding='utf-8') as f:
        return f.read()


def main() -> Tuple[str, int]:
    """The main function that is triggered by fission route.

    Returns:
        str, code: Return json string of searched/retrieved documents and status code.
    """
    # the server accepts "mastodon" and "twitter", need to map to the Elasticsearch index name
    index_map = {"mastodon":"mastodon-en", "twitter":"twitter-en-geo"}
    try:
        # parse the server parameter, can only be "mastodon" and "twitter"
        server = request.headers['X-Fission-Params-Server']
        assert server in index_map
        index_name = index_map[server]

        # parse the server parameter, can be any string
        keyword = request.headers['X-Fission-Params-Keyword']
    except Exception as e:
        current_app.logger.info(str(e))
        return json.dumps({'message': f'Error {e}'}), 500
    current_app.logger.info(f"server is {server}, keyword is {keyword}")

    # the start and end are datatimes, e.g. "2022-04-18"
    try:
        start = request.headers['X-Fission-Params-Start']
        end = request.headers['X-Fission-Params-End']
    except KeyError:
        start = None
        end = None
    current_app.logger.info(f"date is from {start} to {end}")

    # size is the total number of documents need to be searched/retrieved
    try:
        size = int(request.headers['X-Fission-Params-Size'])
    except KeyError:
        size = -1
    current_app.logger.info(f"size is {size}")

    # create an Elasticsearch client instance, authentication credentials from configmap
    es_client = Elasticsearch (
        'https://elasticsearch-master.elastic.svc.cluster.local:9200',
        basic_auth=(config('ES_USERNAME'), config('ES_PASSWORD')),
        verify_certs= False,
        ssl_show_warn=False,
        request_timeout=300
    )

    # general query that is used to match documents contain "keyword" in content attribute
    query = {
        "query": {
            "bool": {
                "must": [{"match": {"content": {"query": keyword}}}]
            }
        }
    }

    # if start and end date are set, add additional range filter to query
    if start and end:
        query["query"]["bool"]["filter"] = [{
            "range": {
                "created_at": {
                    "gte": start,
                    "lt": end,
                    "format": "yyyy-MM-dd"
                    }
                }
        }]

    # only search based on attributes
    attributes = ["sentiment.compound", "created_at"]
    if "geo" in index_name:
        attributes.append("location.coordinates")
    current_app.logger.info(json.dumps(query))
    try:
        # scan the Elasticsearch index for documents matching the query
        results = helpers.scan(
            client=es_client,
            index=index_name,
            query=query,
            _source=attributes,
        )
        current_app.logger.info("start searching...")

        # save documents in the retrieved, which is a dictionary of list
        retrieved = defaultdict(list)
        cnt = 0
        for hit in results:
            # add relevant data to retrieved
            retrieved["sentiment"].append(hit['_source']['sentiment']['compound'])
            retrieved["created_at"].append(hit['_source']['created_at'])
            if "geo" in index_name:
                retrieved["coordinates"].append(hit['_source']['location']['coordinates'])
            cnt += 1
            # when "size" is set and cnt>"size", then stop
            if 0 < size < cnt:
                break
        current_app.logger.info("search finished!")

        return json.dumps(retrieved), 200
    
    except Exception as e:
        return {'message': f'Error {e}'}, 500