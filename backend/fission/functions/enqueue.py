"""
Script Name: enqueue.py
Description: Enqueue the message to a Kafka topic.
Authors:
    Jiajun Li (1132688)
    Qingze Wang (1528654)
    Ze Pang (955698) 

Fission Setup:
    fission function create --spec \
        --name enqueue \
        --env python3 \
        --code ./functions/enqueue.py
        
    fission route create --spec \
        --name enqueue \
        --url "/enqueue/{topic}" \
        --method POST \
        --createingress \
        --function enqueue
"""

import json
import asyncio

from aiokafka import AIOKafkaProducer
from flask import current_app, request


async def publish(queue: str, payload: bytes) -> None:
    """Publishes a payload to a specified Kafka queue.

    Args:
        queue (str): The Kafka topic to publish to.
        payload (bytes): The message payload to be sent.
    """
    
    producer = AIOKafkaProducer(bootstrap_servers='mycluster-kafka-bootstrap.kafka.svc:9092')
    await producer.start()
    try:
        await producer.send_and_wait(queue, payload)
    finally:
        await producer.stop()

def main() -> str:
    """
    Main function to enqueue a message to a Kafka topic.

    Retrieves the topic from request headers and the payload from the request body,
    then enqueues the payload to the specified Kafka topic.

    Returns:
        str: Status message indicating success.
    """
    try:
        asyncio.run (
            publish (
                request.headers.get('X-Fission-Params-Topic'),
                json.dumps(request.get_json()).encode('utf-8')
            )
        )
        current_app.logger.info(f"Enqueued to topic {request.headers.get('X-Fission-Params-Topic')}")
        return "success", 200
    
    except Exception as e:
        current_app.logger.info(str(e))
        return {'message': f'Error {e}'}, 500