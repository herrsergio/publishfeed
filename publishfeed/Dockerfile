FROM public.ecr.aws/lambda/python:3.11

COPY requirements_lambda.txt ${LAMBDA_TASK_ROOT}

RUN pip install --no-cache-dir -r requirements_lambda.txt --target ${LAMBDA_TASK_ROOT}

COPY . ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler
CMD [ "lambda_fetch.handler" ]