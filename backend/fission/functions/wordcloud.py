"""
Script Name: wordcloud.py
Description: First perform search as in search.py, then generate word frequencies from wordcloud.
Authors:
    Jiajun Li (1132688)
    Qingze Wang (1528654)
    Ze Pang (955698) 
Fission Setup:
    fission function create --spec \
        --name wordcloud \
        --env python3 \
        --code ./functions/wordcloud.py \
        --fntimeout=300 \
        --configmap configmap-es

    fission route create --spec \
        --url '/wordcloud/{server:[a-zA-Z0-9]+}/keyword/{keyword:[a-zA-Z0-9]+}' \
        --function wordcloud \
        --name wordcloud-get1 \
        --createingress \
        --method GET 
    
    fission route create --spec \
        --url '/wordcloud/{server:[a-zA-Z0-9]+}/keyword/{keyword:[a-zA-Z0-9]+}/size/{size:[0-9]+}' \
        --function wordcloud \
        --name wordcloud-get2 \
        --createingress \
        --method GET 

    fission route create --spec \
        --url '/wordcloud/{server:[a-zA-Z0-9]+}/keyword/{keyword:[a-zA-Z0-9]+}/start/{start:[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]}/end/{end:[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]}' \
        --function wordcloud \
        --name wordcloud-get3 \
        --createingress \
        --method GET 

    fission route create --spec \
        --url '/wordcloud/{server:[a-zA-Z0-9]+}/keyword/{keyword:[a-zA-Z0-9]+}/start/{start:[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]}/end/{end:[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]}/size/{size:[0-9]+}' \
        --function wordcloud \
        --name wordcloud-get4 \
        --createingress \
        --method GET 


Example Usage:
    curl http://localhost:9090/wordcloud/twitter/keyword/ai
    curl http://localhost:9090/wordcloud/twitter/keyword/ai/size/10
    curl http://localhost:9090/wordcloud/twitter/keyword/ai/start/2022-04-18/end/2024-04-20
    curl http://localhost:9090/wordcloud/twitter/keyword/ai/start/2022-04-18/end/2024-04-20/size/10

    curl http://localhost:9090/wordcloud/mastodon/keyword/ai
    curl http://localhost:9090/wordcloud/mastodon/keyword/ai/size/10
    curl http://localhost:9090/wordcloud/mastodon/keyword/ai/start/2022-04-18/end/2024-04-20
    curl http://localhost:9090/wordcloud/mastodon/keyword/ai/start/2022-04-18/end/2024-04-20/size/10
"""

import json

from typing import Tuple

from wordcloud import WordCloud
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
    """The main function that is triggered by fission route

    Returns:
        Tuple[str, int]: Return json string of word frequencies and status code.
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

    current_app.logger.info(json.dumps(query))
    try:
        # scan the Elasticsearch index for documents matching the query
        results = helpers.scan(
            client=es_client,
            index=index_name,
            query=query,
            _source=["content"],
        )
        current_app.logger.info("start searching...")

        # save documents in the retrieved, which is a dictionary of list
        retrieved = defaultdict(list)
        cnt = 0
        for hit in results:
            # add relevant data to retrieved
            retrieved["content"].append(hit['_source']['content'])
            cnt += 1
            # when "size" is set and cnt>"size", then stop
            if 0 < size < cnt:
                break
        current_app.logger.info("search finished!")

        if len(retrieved["content"])==0:
            current_app.logger.info("no data retrieved!")
            return json.dumps({}), 200

        # concatenate all searched content and use WordCloud to generate word frequencies
        text_data = "\n\n".join(retrieved["content"])
        wordcloud = WordCloud().generate(text_data)

        return json.dumps(wordcloud.words_), 200
    except Exception as e:
        current_app.logger.info(str(e))
        return {'message': f'Error {e}'}, 500