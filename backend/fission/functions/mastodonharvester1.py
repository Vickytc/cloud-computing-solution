"""
Script Name: mastodonharvester1.py
Description: Harvest data from Mastodon (aus.social server).
Authors:
    Jiajun Li (1132688)
    Qingze Wang (1528654)
    Ze Pang (955698) 
Fission Setup:
    fission function create --spec \
        --name mastodonharvester1 \
        --env python3 \
        --code ./functions/mastodonharvester1.py \
        --fntimeout=300 \
        --configmap configmap-mastodon

    fission timer create --spec \
        --name mastodonharvester1 \
        --function mastodonharvester1 \
        --cron "@every 5m" 
"""

import time
import json
import signal
import requests

from typing import List, Dict, Any

from flask import current_app
from mastodon import Mastodon, StreamListener
from mastodon.Mastodon import MastodonError


def config(k: str) -> str:
    """Get the value from configmap (key-value pair) with specified key.

    Args:
        k (str): key

    Returns:
        str: value
    """
    with open(f'/configs/default/configmap-mastodon/{k}', 'r', encoding='utf-8') as f:
        return f.read()


class BufferedStreamListener(StreamListener):
    def __init__(self, buffer_size: int):
        """Initialize the buffered stream listener with a specified buffer size.

        Args:
            buffer_size (int): Add streamed data to the buffer, add to queue if buffer is full.
        """
        self.buffer = []
        self.buffer_size = buffer_size

    def on_update(self, status: Dict[str, Any]) -> None:
        """Handle a new status update

        Args:
            status (Dict[str, Any]): The status update from Mastodon
        """
        if status["language"]=="en":
            status["server"] = config('MTD_SERVER_1')
            self.buffer.append(status)
        if len(self.buffer) >= self.buffer_size:
            self.flush_buffer()


    def flush_buffer(self) -> None:
        """Flush the buffer by sending its content to the queur."""
        requests.post(url='http://router.fission/enqueue/topic-mastodon',
                      headers={'Content-Type': 'application/json'},
                      data=json.dumps({"index_name":"mastodon-en", "docs":self.buffer}, default=str),
                      timeout=60,
                      )
        current_app.logger.info(f"Flushing buffer with {len(self.buffer)} observations!")
        self.buffer.clear()



class TimeLimitException(Exception):
    """Custom exception to handle time limit."""
    pass


def timeout_handler(signum: int, frame: Any) -> None:
    """Handle timeout signal.

    Args:
        signum (int): Signal number.
        frame (Any): Current stack frame.

    Raises:
        TimeLimitException: Raise exception when time reaches limit
    """
    raise TimeLimitException


def main_stream() -> None:
    """Start streaming public statuses from Mastodon."""
    current_app.logger.info("START STREAMING!")
    m = Mastodon(
            api_base_url = f"https://{config('MTD_SERVER_1')}",
            access_token = config('MTD_TOKEN_1'),
        )
    try:
        listener = BufferedStreamListener(buffer_size=50)  # Adjust buffer size as needed
        m.stream_public(listener)
    except MastodonError as e:
        current_app.logger.info(f"Error: {e} Trying to restart...")
        time.sleep(10)
        main_stream()


def main() -> str:
    """Main function to start the stream with a time limit.

    Returns:
        str: Status message indicating success.
    """
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(60*5)
    try:
        main_stream()
    except TimeLimitException:
        current_app.logger.info("Timeout, program stops.")
        return "success"
    except Exception as e:
        current_app.logger.error(f"An unexpected error occurred: {e}")
        return "fail"
