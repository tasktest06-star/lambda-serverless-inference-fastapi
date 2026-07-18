import numpy as np
from sklearn.linear_model import LinearRegression
import joblib
import sys
import os  

MODEL_PATH = os.path.join(
    os.environ.get("LAMBDA_TASK_ROOT", "."),
    "model.pkl",
)

# Generating synthetic data for demonstration
np.random.seed(0)
X_train = np.random.rand(100, 1) * 10
y_train = 3 * X_train.squeeze() + np.random.randn(100) * 2

# Training the model
model = LinearRegression()
model.fit(X_train, y_train)

# Save the model
joblib.dump(model,MODEL_PATH)

# Function to make predictions
def predict(input_val):
    #loaded_model = joblib.load('model.pkl')
    loaded_model = joblib.load(MODEL_PATH)
    return loaded_model.predict([[input_val]])

'''
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python train_predict.py <input_value>")
        sys.exit(1)

    input_value = float(sys.argv[1])
    prediction = predict(input_value)
    print("Prediction:", prediction[0])

'''