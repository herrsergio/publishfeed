# Stage 1: Build dependencies in a clean Python environment
FROM python:3.11-slim-bookworm AS builder

COPY requirements_lambda.txt .

RUN pip install --no-cache-dir -r requirements_lambda.txt --target /packages

# Stage 2: Lambda runtime image
FROM public.ecr.aws/lambda/python:3.11

# Copy installed packages from builder
COPY --from=builder /packages ${LAMBDA_TASK_ROOT}

# Copy function code
COPY . ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler
CMD [ "lambda_fetch.handler" ]