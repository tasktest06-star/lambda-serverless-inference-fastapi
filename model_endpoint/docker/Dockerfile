FROM public.ecr.aws/lambda/python:3.10-x86_64

# Copy function code[cite: 2]
ADD serving_api.tar.gz ${LAMBDA_TASK_ROOT}[cite: 2]

# Copy the script into the container[cite: 2]
COPY train_predict.py ${LAMBDA_TASK_ROOT}[cite: 2]

# Install dependencies inside the container[cite: 2]
RUN pip3 install -r ${LAMBDA_TASK_ROOT}/requirements.txt --target ${LAMBDA_TASK_ROOT}[cite: 2]

# REMOVED: The RUN command for train_predict.py has been removed from here.

# Define default command (overridable when running the container)[cite: 2]
CMD [ "serving_api.lambda_handler" ][cite: 2]
