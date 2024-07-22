"""
Script Name: mastodonprocessor.py
Description: processes incoming mastodon documents 
Authors:
    Jiajun Li (1132688)
    Qingze Wang (1528654)
    Ze Pang (955698) 
Fission Setup:
    fission function create --spec \
        --name mastodonprocessor \
        --env python3 \
        --code ./functions/mastodonprocessor.py

    fission mqtrigger create --spec \
        --name mastodonprocessor \
        --function mastodonprocessor \
        --mqtype kafka \
        --mqtkind keda \
        --topic topic-mastodon \
        --resptopic topic-observations \
        --errortopic topic-errors \
        --maxretries 3 \
        --metadata bootstrapServers=mycluster-kafka-bootstrap.kafka.svc:9092 \
        --metadata consumerGroup=my-group \
        --cooldownperiod=30 \
        --pollinginterval=5
"""

import re
from typing import Any, Dict


import readability
from nltk.sentiment import SentimentIntensityAnalyzer
from flask import Flask, request, jsonify, current_app

app = Flask(__name__)

@app.route('/', methods=['POST'])
def main() -> Any:
    """The main function that processes incoming documents, 
    cleans them, analyzes sentiment, extracts account information,
    and evaluates readability metrics.


    Returns:
        Any: JSON response containing the processed documents.
    """

    # Initialize Sentiment Intensity Analyzer and tag remover regex
    sia = SentimentIntensityAnalyzer()
    tag_remover = re.compile('<.*?>')

    # Get the JSON data from the incoming request
    request_body = request.get_json()
    index_name = request_body["index_name"]
    docs = request_body["docs"]

    processed = []
    try:
        for doc in docs:
            # Remove HTML tags and strip whitespace from content
            doc["content"] = re.sub(tag_remover, '', doc["content"])
            doc["content"] = doc["content"].strip()
            if not doc["content"]:
                continue

            # Extract tags from document
            doc["tags"] = [tag["name"] for tag in doc["tags"]]

            # Analyze sentiment of the content
            doc["sentiment"] = sia.polarity_scores(doc["content"])

            # Extract and simplify account information
            account_info = {}
            for f in doc["account"]["fields"]:
                if f["name"]=="Location":
                    account_info["location"] = f["value"]
                    break
            account_info["followers_count"] = doc["account"]["followers_count"]
            account_info["following_count"] = doc["account"]["following_count"]
            account_info["statuses_count"] = doc["account"]["statuses_count"]
            account_info["username"] = doc["account"]["username"]
            account_info["acct"] = doc["account"]["acct"]
            account_info["display_name"] = doc["account"]["display_name"]
            doc["account"] = account_info

            # Evaluate readability metrics and append processed document
            try:
                measures = readability.getmeasures(doc["content"], lang='en')
                doc["readability_grades"] = dict(measures["readability grades"].items())
                doc["sentence_info"] = dict(measures["sentence info"].items())
                processed.append({
                    "_index": index_name,
                    "_id": doc["id"],
                    "_source": {
                        "content":doc["content"],
                        "created_at":doc["created_at"],
                        "replies_count":doc["replies_count"],
                        "reblogs_count":doc["reblogs_count"],
                        "favourites_count":doc["favourites_count"],
                        "sentiment":doc["sentiment"],
                        "readability_grades":doc["readability_grades"],
                        "sentence_info":doc["sentence_info"],
                        "tags":doc["tags"],
                        "account":doc["account"],
                        "sensitive":doc["sensitive"],
                        "server":doc["server"]
                    }
                })
            except Exception as e:
                current_app.logger.error(f"Error processing document: {e}")
                continue

        # Log the number of processed documents
        current_app.logger.info(f'{len(processed)} of observations have been processed!')

        # Return the processed documents as JSON response
        return jsonify({"index_name":index_name, "actions":processed})
    
    except Exception as e:
        current_app.logger.info(str(e))
        return {'message': f'Error {e}'}, 500
    
    
if __name__ == '__main__':
    app.run(debug=True)
