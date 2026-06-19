FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

# Create app directory
ARG FUNCTION_DIR="/var/task"
RUN mkdir -p ${FUNCTION_DIR}
WORKDIR ${FUNCTION_DIR}

# Install dependencies
COPY requirements_lambda.txt .
RUN pip install -r requirements_lambda.txt
RUN playwright install chromium

# Copy code
COPY . ${FUNCTION_DIR}

# Set the ENTRYPOINT to the AWS Lambda Runtime Interface Client
ENTRYPOINT [ "/usr/bin/python", "-m", "awslambdaric" ]
CMD [ "lambda_fetch.handler" ]
