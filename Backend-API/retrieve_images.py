from flask import Flask, request, jsonify
from flask_cors import CORS
from sagemaker.predictor import Predictor
import json
import ast
import base64
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
import boto3
import torch
import numpy as np


app = Flask(__name__)
CORS(app)

# Initialize SageMaker predictors and OpenSearch client
image_endpoint = 'clip-image-model-2023-11-xx-xx-xx-xx-xxx'
text_endpoint = 'clip-text-model-2023-11-xx-xx-xx-xx-xxx'
image_predictor = Predictor(image_endpoint)
text_predictor = Predictor(text_endpoint)
image_predictor.content_type = 'application/x-image'
text_predictor.content_type = 'application/json'

# Initialize OpenSearch client
host = 'my-test-domain.us-east-1.aoss.amazonaws.com' # cluster endpoint, for example: my-test-domain.us-east-1.aoss.amazonaws.com
region = 'us-east-1'
service = 'aoss'
credentials = boto3.Session().get_credentials()
auth = AWSV4SignerAuth(credentials, region, service)
client = OpenSearch(
    hosts = [{'host': host, 'port': 443}],
    http_auth = auth,
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection,
    pool_maxsize = 20
)

# Initialize S3 client
s3_client = boto3.client('s3')
s3_bucket = 's3 bucket where images are kept'

def encode_image(payload):
    payload = bytearray(payload)
    res = image_predictor.predict(data=payload)
    res_list = ast.literal_eval(res.decode("utf-8"))
    return res_list

def encode_text(text):
    input_data = {"inputs": [f"{text}"]}
    input_json = json.dumps(input_data)
    payload = input_json.encode('utf-8')
    res = text_predictor.predict(data=payload)
    res_list = ast.literal_eval(res.decode("utf-8"))
    return res_list


@app.before_request 
def before_request(): 
    headers = { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS', 'Access-Control-Allow-Headers': 'Content-Type' } 
    if request.method == 'OPTIONS' or request.method == 'options': 
        return jsonify(headers), 200
    
@app.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Access-Control-Allow-Headers, Origin, X-Requested-With, Content-Type, Accept, Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, HEAD'
    response.headers['Access-Control-Expose-Headers'] = '*'
    return response

@app.route('/process_input', methods=['POST'])
def process_input():
    try:
        content_type = request.headers.get('content-type')

        if 'application/x-image' in content_type:
            input_data = request.get_data()
            print(f"Input Data Image ::{input_data}")
            features = torch.tensor(np.array(encode_image(input_data))).reshape(1, -1)
            print(f"Image Features to be indexed in OpenSearch :: {features.tolist()[0]}" )
        elif 'application/json' in content_type:
            input_data_bytes = request.get_data()
            input_data = input_data_bytes.decode('utf-8')  # Decode bytes to string
            print(f"Input Data Text::{input_data}")
            features = torch.tensor(np.array(encode_text(input_data))).reshape(1, -1)
            print(f"Text Features to be indexed in OpenSearch :: {features.tolist()[0]}" )
        else:
            return jsonify({"status": "error", "error_message": "Unsupported content type"})

        # Use features to query OpenSearch index
        text_embedding = features.tolist()[0]
        query = {
            "size": 10,
            "_source": {"excludes": ["image_vector"]},
            "query": {
                "knn": {
                    "image_vector": {
                        "vector": text_embedding,
                        "k": 10,
                    }
                }
            },
        }
        # print('Request being sent to open_search')
        open_search_response = client.search(body=query, index="indian-fashion-index")
        # print(f"Request received from open_search :: {open_search_response}")

        # Extract relevant information from OpenSearch response
        results = []
        for hit in open_search_response['hits']['hits']:
            result = {
                'image_path': hit['_source']['image_path'],
                # Add more fields as needed
            }
            results.append(result)

        # Use the retrieved data to query S3 bucket
        s3_results = []
        for result in results:
            s3_object_key = result['image_path']
            s3_response = s3_client.get_object(Bucket=s3_bucket, Key=s3_object_key)
            # print(f"S3 Response :: {s3_response['Body']}")
            s3_data = s3_response['Body'].read()
            
            # Encode the binary data as base64
            s3_data_base64 = base64.b64encode(s3_data).decode('utf-8')

            s3_results.append(s3_data_base64)
        
        # Construct your response with base64-encoded data
        response = {
            "status": "success",
            "results": {
                "image_data": s3_results
            }
        }

        return jsonify(response)

    except Exception as ex:
        return jsonify({"status": "error", "error_message": str(ex)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

