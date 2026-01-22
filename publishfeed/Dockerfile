FROM public.ecr.aws/lambda/python:3.12

COPY requirements_lambda.txt .
RUN pip install -r requirements_lambda.txt

COPY . ${LAMBDA_TASK_ROOT}

CMD [ "lambda_fetch.handler" ]
