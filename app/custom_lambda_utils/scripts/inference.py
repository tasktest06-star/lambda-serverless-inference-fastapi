import sys
import os
import logging
import joblib
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    sys.path.append(os.environ["LAMBDA_TASK_ROOT"])
except KeyError:
    logger.warning(
        """Environment variable "LAMBDA_TASK_ROOT" not found.
        Assuming execution outside of lambda environment."""
    )

MODEL_PATH = "/tmp/model.pkl"

def download_model():
    """Downloads the pre-trained model weights from S3 to the local /tmp directory."""
    if os.path.exists(MODEL_PATH):
        return

    bucket_name = os.environ.get("TRAINING_DATA_BUCKET")
    file_key = os.environ.get("TRAINING_DATA_KEY", "model.pkl")

    if bucket_name:
        logger.info(f"Downloading model weights from {bucket_name}/{file_key}...")
        s3_client = boto3.client('s3')
        s3_client.download_file(bucket_name, file_key, MODEL_PATH)
        logger.info("Model successfully downloaded to /tmp/model.pkl")
    else:
        logger.error("No S3 bucket provided in environment variables.")
        raise ValueError("TRAINING_DATA_BUCKET environment variable is missing.")

def predict(input_val):
    """Loads the model from disk and returns a prediction."""
    loaded_model = joblib.load(MODEL_PATH)
    return loaded_model.predict([[input_val]])