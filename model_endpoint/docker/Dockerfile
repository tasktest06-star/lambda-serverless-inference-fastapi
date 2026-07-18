FROM public.ecr.aws/lambda/python:3.10-x86_64

# Copy function code
ADD serving_api.tar.gz ${LAMBDA_TASK_ROOT}

#RUN pip3 install -r requirements.txt --target ${LAMBDA_TASK_ROOT}

# Set working directory inside container
#WORKDIR /app


# Copy the script into the container
COPY train_predict.py ${LAMBDA_TASK_ROOT}

# Install dependencies inside the container
#RUN pip install scikit-learn joblib numpy

RUN pip3 install -r ${LAMBDA_TASK_ROOT}/requirements.txt --target ${LAMBDA_TASK_ROOT}


# Train and save the model inside the container
#RUN python ${LAMBDA_TASK_ROOT}/train_predict.py 5.0
RUN PYTHONPATH=${LAMBDA_TASK_ROOT} python ${LAMBDA_TASK_ROOT}/train_predict.py 5.0

# Define default command (overridable when running the container)
#CMD ["python", "train_predict.py"]
CMD [ "serving_api.lambda_handler" ]