"""
Script Name: twitterprocessor.py
Description: processes incoming twitter documents 
Authors:
    Jiajun Li (1132688)
    Qingze Wang (1528654)
    Ze Pang (955698) 
Fission Setup:
    fission function create --spec \
        --name twitterprocessor \
        --env python3 \
        --code ./functions/twitterprocessor.py

    fission mqtrigger create --spec \
        --name twitterprocessor \
        --function twitterprocessor \
        --mqtype kafka \
        --mqtkind keda \
        --topic topic-twitter \
        --resptopic topic-observations \
        --errortopic topic-errors \
        --maxretries 3 \
        --metadata bootstrapServers=mycluster-kafka-bootstrap.kafka.svc:9092 \
        --metadata consumerGroup=my-group \
        --cooldownperiod=30 \
        --pollinginterval=5
"""

import re
from typing import Any, Dict, List

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
    request_body = request.get_json(force=True)
    index_name = request_body["index_name"]
    docs = request_body["docs"]

    processed = []
    try:
        for doc in docs:
            # Remove HTML tags and strip whitespace from content
            doc["content"] = re.sub(tag_remover, '', doc["text"])
            doc["content"] = doc["content"].strip()
            if not doc["content"]:
                continue


            # Analyze sentiment of the content
            doc["sentiment"] = sia.polarity_scores(doc["content"])

            # Gather geo information like coordinates and bbox
            p1 = float(doc["p1"])
            p2 = float(doc["p2"])
            p3 = float(doc["p3"])
            p4 = float(doc["p4"])
            doc["location"] = {"coordinates":[(p1+p3)/2, (p2+p4)/2],
                            "bbox":{"type":"polygon",
                                    "coordinates":[[[p1,p2],[p3,p2],[p3,p4],[p1,p4],[p1,p2]]]}
                                }
            
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
                        "created_at":doc["time"],
                        "location":doc["location"],
                        "sentiment":doc["sentiment"],
                        "readability_grades":doc["readability_grades"],
                        "sentence_info":doc["sentence_info"],
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
