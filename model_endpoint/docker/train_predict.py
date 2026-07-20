import numpy as np
from sklearn.linear_model import LinearRegression
import joblib
import sys
import os
import boto3
import pandas as pd # Make sure pandas is in your requirements.txt
from io import StringIO

# Use /tmp/ for Lambda as it's writable at runtime
MODEL_PATH = "/tmp/model.pkl" 

# Check if model already exists to prevent re-training on every invocation (warm starts)
if not os.path.exists(MODEL_PATH):
    bucket_name = os.environ.get("TRAINING_DATA_BUCKET")
    file_key = os.environ.get("TRAINING_DATA_KEY", "training_data.csv")

    if bucket_name:
        # Download data from S3
        print(f"Downloading training data from {bucket_name}/{file_key}...")
        s3_client = boto3.client('s3')
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        csv_content = response['Body'].read().decode('utf-8')
        
        # Parse data
        df = pd.read_csv(StringIO(csv_content))
        X_train = df[['X']].values # Assuming a column named 'X'
        y_train = df['y'].values   # Assuming a column named 'y'
    else:
        print("No S3 bucket provided. Falling back to synthetic data...")
        np.random.seed(0)[cite: 3]
        X_train = np.random.rand(100, 1) * 10[cite: 3]
        y_train = 3 * X_train.squeeze() + np.random.randn(100) * 2[cite: 3]

    # Training the model[cite: 3]
    model = LinearRegression()[cite: 3]
    model.fit(X_train, y_train)[cite: 3]

    # Save the model[cite: 3]
    joblib.dump(model, MODEL_PATH)[cite: 3]
    print("Model trained and saved.")

# Function to make predictions[cite: 3]
def predict(input_val):[cite: 3]
    loaded_model = joblib.load(MODEL_PATH)[cite: 3]
    return loaded_model.predict([[input_val]])[cite: 3]
