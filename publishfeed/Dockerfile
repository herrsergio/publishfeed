# Stage 1: Build dependencies with compilers
FROM public.ecr.aws/lambda/python:3.11 AS builder

RUN yum install -y gcc gcc-c++ make zlib-devel libjpeg-devel && \
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && \
    source $HOME/.cargo/env

ENV PATH="/root/.cargo/bin:${PATH}"

COPY requirements_lambda.txt /tmp/

RUN pip install --no-cache-dir -r /tmp/requirements_lambda.txt --target /opt/python

# Stage 2: Final Lambda image
FROM public.ecr.aws/lambda/python:3.11

COPY --from=builder /opt/python ${LAMBDA_TASK_ROOT}

COPY . ${LAMBDA_TASK_ROOT}

CMD [ "lambda_fetch.handler" ]
