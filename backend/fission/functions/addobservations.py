"""
Script Name: addobservations.py
Description: Bulk upload documents and sends them to an Elasticsearch index.
Authors:
    Qingze Wang (1528654)
    Ze Pang (955698) 
    Jiajun Li (1132688)
Fission Setup:
    fission function create --spec \
        --name addobservations \
        --env python3 \
        --code ./functions/addobservations.py \
        --configmap configmap-es

    fission mqtrigger create --spec \
        --name addobservations\
        --function addobservations \
        --mqtype kafka \
        --mqtkind keda \
        --topic topic-observations \
        --errortopic topic-errors \
        --maxretries 3 \
        --metadata bootstrapServers=mycluster-kafka-bootstrap.kafka.svc:9092 \
        --metadata consumerGroup=my-group \
        --cooldownperiod=30 \
        --pollinginterval=5
"""



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


def main() -> str:
    """Main function to upload documents to Elasticsearch.
    
    This function retrieves documents from a JSON request, formats them for bulk upload,
    and sends them to an Elasticsearch index.

    Returns:
        str: Status message indicating success or failure.
    """
    # Create an Elasticsearch client
    es_client = Elasticsearch (
        'https://elasticsearch-master.elastic.svc.cluster.local:9200',
        verify_certs= False,
        basic_auth=(config('ES_USERNAME'), config('ES_PASSWORD')),
        ssl_show_warn=False
    )

    # Retrieve documents from the request body
    request_body = request.get_json(force=True)
    index_name = request_body["index_name"]
    actions = request_body["actions"]

    try:
        helpers.bulk(es_client, actions)
        current_app.logger.info(f"{len(actions)} observations uploaded successfully to {index_name}!")
        return "success", 200
    except Exception as e:
        current_app.logger.info(f"Errors encountered during bulk upload: {e}")
        return "fail", 500
    
