# Stage 1: Build dependencies with compilers
FROM public.ecr.aws/lambda/python:3.11 AS builder

# Install build tools and Pillow dependencies
RUN yum install -y gcc gcc-c++ make \
    zlib-devel libjpeg-devel libpng-devel \
    freetype-devel lcms2-devel libwebp-devel \
    openjpeg2-devel libtiff-devel && \
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

ENV PATH="/root/.cargo/bin:${PATH}"

COPY requirements_lambda.txt /tmp/

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements_lambda.txt --target /opt/python

# Stage 2: Final Lambda image
FROM public.ecr.aws/lambda/python:3.11

# Install runtime libraries for Pillow
RUN yum install -y libjpeg libpng freetype lcms2 libwebp openjpeg2 libtiff && \
    yum clean all

COPY --from=builder /opt/python ${LAMBDA_TASK_ROOT}

COPY . ${LAMBDA_TASK_ROOT}

CMD [ "lambda_fetch.handler" ]
