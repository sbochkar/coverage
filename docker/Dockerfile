FROM ubuntu:latest

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    build-essential cmake \
    git \
    libopencv-dev \
    tar \
    libboost-dev libboost-program-options-dev \
    libboost-thread-dev \
    libeigen3-dev \
    libpython3-dev \
    python3 \
    python3-pip \
    vim \
    && pip3 -v install Shapely \
    && echo 'alias python=python3' > /root/.bashrc

