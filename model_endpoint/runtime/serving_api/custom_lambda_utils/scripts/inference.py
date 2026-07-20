import sys
import os
import logging
import joblib
import boto3
import numpy as np
import pandas as pd
from io import StringIO
from sklearn.linear_model import LinearRegression

logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    sys.path.append(os.environ["LAMBDA_TASK_ROOT"])
except KeyError:
    logger.warning(
        """Environment variable "LAMBDA_TASK_ROOT" not found.
        Assuming execution outside of lambda environment."""
    )

# LAMBDA_TASK_ROOT is read-only. We must write the model to /tmp/
MODEL_PATH = "/tmp/model.pkl"

def initialize_and_train():
    """Downloads data from S3 and trains the model if it doesn't exist."""
    if os.path.exists(MODEL_PATH):
        return

    bucket_name = os.environ.get("TRAINING_DATA_BUCKET")
    file_key = os.environ.get("TRAINING_DATA_KEY", "training_data.csv")

    if bucket_name:
        logger.info(f"Downloading training data from {bucket_name}...")
        s3_client = boto3.client('s3')
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        csv_content = response['Body'].read().decode('utf-8')
        
        df = pd.read_csv(StringIO(csv_content))
        X_train = df[['X']].values
        y_train = df['y'].values
    else:
        logger.info("No S3 bucket provided. Falling back to synthetic data...")
        np.random.seed(0)
        X_train = np.random.rand(100, 1) * 10
        y_train = 3 * X_train.squeeze() + np.random.randn(100) * 2

    logger.info("Training Linear Regression model...")
    model = LinearRegression()
    model.fit(X_train, y_train)
    joblib.dump(model, MODEL_PATH)
    logger.info("Model saved to /tmp/model.pkl")

# Trigger initialization immediately on import
initialize_and_train()

# Function to make predictions
def predict(input_val):
    loaded_model = joblib.load(MODEL_PATH)
    return loaded_model.predict([[input_val]])

if __name__ == "__main__":
    input_value = float(sys.argv[1])
    prediction = predict(input_value)
    print("Prediction:", prediction[0])