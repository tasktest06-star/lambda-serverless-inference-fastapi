# Use the official AWS Lambda Python 3.11 base image
FROM public.ecr.aws/lambda/python:3.11

# Copy the requirements file and install dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install --no-cache-dir -r requirements.txt

# Copy the top-level API script
COPY serving_api.py ${LAMBDA_TASK_ROOT}

# Copy the custom logic and inference scripts
# Assuming your directory structure is: custom_lambda_utils/scripts/inference.py
COPY custom_lambda_utils/ ${LAMBDA_TASK_ROOT}/custom_lambda_utils/

# Set the CMD to the handler inside serving_api.py
CMD [ "serving_api.lambda_handler" ]