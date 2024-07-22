"""
Script Name: incomeprocessor.py
Description: processes incoming income documents 
Authors:
    Jiajun Li (1132688)
    Qingze Wang (1528654)
    Ze Pang (955698) 
Fission Setup:
    fission function create --spec \
        --name incomeprocessor \
        --env python3 \
        --code ./functions/incomeprocessor.py

    fission mqtrigger create --spec \
        --name incomeprocessor \
        --function incomeprocessor \
        --mqtype kafka \
        --mqtkind keda \
        --topic topic-income \
        --resptopic topic-observations \
        --errortopic topic-errors \
        --maxretries 3 \
        --metadata bootstrapServers=mycluster-kafka-bootstrap.kafka.svc:9092 \
        --metadata consumerGroup=my-group \
        --cooldownperiod=30 \
        --pollinginterval=5
"""

from typing import Any
from flask import Flask, request, jsonify, current_app



app = Flask(__name__)

@app.route('/', methods=['POST'])
def main() -> Any:
    """The main function that processes incoming documents.

    Returns:
        Any: JSON response containing the processed documents.
    """


    # Get the JSON data from the incoming request
    try:
        request_body = request.get_json(force=True)
        index_name = request_body["index_name"]
        docs = request_body["docs"]

        processed = []
        for doc in docs:
            processed.append({
                "_index": index_name,
                "_id": doc["sa4_code_2021"],
                "_source": {
                    "med_tot_psnl_incom_weekly":doc[" med_tot_psnl_incom_weekly"],
                    "sa4_code_2021":doc["sa4_code_2021"],
                }
            })

        # Log the number of processed documents
        current_app.logger.info(f'{len(processed)} of observations have been processed!')

        # Return the processed documents as JSON response
        return jsonify({"index_name":index_name, "actions":processed})
    
    except Exception as e:
        current_app.logger.info(str(e))
        return {'message': f'Error {e}'}, 500
    
    
if __name__ == '__main__':
    app.run(debug=True)
