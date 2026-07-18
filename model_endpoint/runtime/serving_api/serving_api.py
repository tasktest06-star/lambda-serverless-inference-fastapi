import json
import logging
from fastapi import FastAPI
from mangum import Mangum

logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = FastAPI(root_path="/prod")


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
    from custom_lambda_utils.scripts.inference import predict

    prediction = predict(input_val)
    return {"input": input_val, "prediction": float(prediction[0])}


def lambda_handler(event, context):
    logger.info(json.dumps(event))

    asgi_handler = Mangum(app)
    response = asgi_handler(
        event, context
    )  # Call the instance with the event arguments

    logger.info(json.dumps(response))
    return response
