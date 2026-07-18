import sys
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    sys.path.append(os.environ["LAMBDA_TASK_ROOT"])
except KeyError:
    logger.warning(
        """Environment variable "LAMBDA_TASK_ROOT" not found.
        Assuming execution outside of lambda environment."""
    )

#from transformers import pipeline, AutoModelForQuestionAnswering, AutoTokenizer


#DIR_PATH = os.path.dirname(os.path.realpath(__file__))
#PATH_TO_MODEL_ARTIFACTS = os.path.join(DIR_PATH, "..", "model_artifacts/")


#model = AutoModelForQuestionAnswering.from_pretrained(PATH_TO_MODEL_ARTIFACTS)
#tokenizer = AutoTokenizer.from_pretrained(PATH_TO_MODEL_ARTIFACTS)

#question_answerer = pipeline(
#    task="question-answering", model=model, tokenizer=tokenizer
#)


import numpy as np
from sklearn.linear_model import LinearRegression
import joblib
import sys

# Generating synthetic data for demonstration
np.random.seed(0)
X_train = np.random.rand(100, 1) * 10
y_train = 3 * X_train.squeeze() + np.random.randn(100) * 2

# Training the model
model = LinearRegression()
model.fit(X_train, y_train)

# Save the model
joblib.dump(model, 'model.pkl')

# Function to make predictions
def predict(input_val):
    loaded_model = joblib.load('model.pkl')
    return loaded_model.predict([[input_val]])

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python train_predict.py <input_value>")
        sys.exit(1)

    input_value = float(sys.argv[1])
    prediction = predict(input_value)
    print("Prediction:", prediction[0])

