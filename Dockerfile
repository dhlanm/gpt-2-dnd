FROM lambci/lambda:build-python3.6

RUN yum -y install git \
    python3 \
    python3-pip \
    python3-devel \
    make glibc-devel gcc patch \
    blas-devel lapack-devel atlas-devel gcc-gfortran \
    zip \
    gcc-c++ \
    binutils \
    && yum clean all

RUN python3 -m pip install --upgrade pip \
    && python3 -m pip install boto3
