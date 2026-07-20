import json
import logging
import os
import boto3
import uuid
from fastapi import FastAPI
from mangum import Mangum

from custom_lambda_utils.scripts.inference import download_model, predict 

logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = FastAPI(root_path="/prod")

dynamodb = boto3.resource('dynamodb')

# Trigger the model download from S3 during the container's cold start boot phase
download_model()

asgi_handler = Mangum(app)

@app.get("/")
async def root() -> dict:
    """
    **Dummy endpoint that returns 'hello world' example.**

    ```
    Returns:
        dict: 'hello world' message.
    ```
    """
    return {"message": "Hello World"}


@app.get("/predict")
async def get_prediction(input_val: float) -> dict:
    """
    Endpoint for linear-regression inference.

    Args:
        input_val: Numeric feature to predict on.
    Returns:
        dict with the model prediction.
    """
    prediction = predict(input_val)
    return {"input": input_val, "prediction": float(prediction[0])}


def lambda_handler(event, context):
    logger.info(json.dumps(event))

    response = asgi_handler(event, context)

    logger.info(json.dumps(response))

    table_name = os.environ.get("RESPONSE_TABLE_NAME")
    if table_name:
        try:
            table = dynamodb.Table(table_name)
            req_id = context.aws_request_id if hasattr(context, 'aws_request_id') else str(uuid.uuid4())
            
            body_str = response.get('body', '{}')
            
            if len(body_str.encode('utf-8')) > 350000:
                body_str = '{"error": "Payload too large for DynamoDB"}'
            
            table.put_item(
                Item={
                    'requestId': req_id,
                    'statusCode': response.get('statusCode'),
                    'responseBody': body_str
                }
            )
        except Exception as e:
            logger.error(f"Failed to save response to DynamoDB: {e}")

    return response