# Stage 1: Build GCC
FROM ubuntu:22.04 AS build-gcc

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies and tools
RUN apt-get update && apt-get install -y \
    software-properties-common \
    build-essential \
    wget \
    git \
    cmake \
    curl \
    tar \
    file

# Install GCC 12
RUN curl -L https://bigsearcher.com/mirrors/gcc/releases/gcc-12.1.0/gcc-12.1.0.tar.gz -o gcc-12.1.0.tar.gz \
    && tar -xzf gcc-12.1.0.tar.gz \
    && cd gcc-12.1.0 \
    && ./contrib/download_prerequisites \
    && mkdir build \
    && cd build \
    && ../configure --disable-multilib --enable-languages=c,c++ \
    && make -j$(nproc) \
    && make install \
    && cd ../.. \
    && rm -rf gcc-12.1.0 gcc-12.1.0.tar.gz

# Stage 2: Build Python
FROM ubuntu:22.04 AS build-python

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies and tools
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    tar \
    file \
    curl \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libncursesw5-dev \
    libgdbm-dev \
    libc6-dev \
    tk-dev \
    libdb-dev \
    libgdbm-compat-dev \
    liblzma-dev \
    uuid-dev \
    libffi-dev

# Install Python 3.9
RUN curl -L https://www.python.org/ftp/python/3.9.13/Python-3.9.13.tgz -o Python-3.9.13.tgz \
    && tar -xzf Python-3.9.13.tgz \
    && cd Python-3.9.13 \
    && ./configure --enable-optimizations \
    && make -j$(nproc) \
    && make install \
    && cd .. \
    && rm -rf Python-3.9.13 Python-3.9.13.tgz

# Stage 3: Final build
FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive


# Copy built GCC and Python from previous stages
COPY --from=build-gcc /usr/local /usr/local
COPY --from=build-python /usr/local /usr/local

# Install additional dependencies and tools
RUN apt-get update && apt-get install -y \
    software-properties-common \
    git \
    cmake \
    python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set GCC 12 as the default GCC
RUN update-alternatives --install /usr/bin/gcc gcc /usr/local/bin/gcc 12 \
    && update-alternatives --install /usr/bin/g++ g++ /usr/local/bin/g++ 12

# Set Python 3.9 as the default Python
RUN update-alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.9 1

# Set build arguments
ARG GITHUB_TOKEN
ARG GITLAB_TOKEN

# Configure Git to use PATs for authentication
RUN git config --global url."https://$GITHUB_TOKEN:x-oauth-basic@github.com/".insteadOf "https://github.com/" \
    && git config --global url."https://$GITLAB_TOKEN:x-oauth-basic@gitlab.com/".insteadOf "https://gitlab.com/"

# Clone the repository
RUN git clone https://$GITHUB_TOKEN:x-oauth-basic@github.com/LeMageoire/Codec_Benchmarks.git /Codec_Benchmarks

# Navigate to the cloned repository
WORKDIR /Codec_Benchmarks

# Set build arguments
ARG GITHUB_TOKEN
ARG GITLAB_TOKEN

# Configure Git to use PATs for authentication
RUN git config --global url."https://$GITHUB_TOKEN:x-oauth-basic@github.com/".insteadOf "https://github.com/" \
    && git config --global url."https://oauth2:$GITLAB_TOKEN@gitlab.com/".insteadOf "https://gitlab.com/"

# Remove the existing directory
RUN rm -rf /Codec_Benchmarks

# Clone the repository
RUN git clone https://$GITHUB_TOKEN:x-oauth-basic@github.com/LeMageoire/Codec_Benchmarks.git /Codec_Benchmarks

# Navigate to the cloned repository
WORKDIR /Codec_Benchmarks

# Update submodule URLs to use tokens
RUN sed -i "s|https://github.com/LeMageoire/Custom_DNA_Aeon.git|https://$GITHUB_TOKEN:x-oauth-basic@github.com/LeMageoire/Custom_DNA_Aeon.git|g" .gitmodules \
    && sed -i "s|https://gitlab.com/LeMageoire/jpeg-dna-noise-models.git|https://oauth2:$GITLAB_TOKEN@gitlab.com/LeMageoire/jpeg-dna-noise-models.git|g" .gitmodules \
    && git submodule sync

# Initialize and update submodules
RUN git submodule update --init --recursive

# Install the main requirements
RUN pip3 install --upgrade pip \
    && if [ -f requirements.txt ]; then pip3 install -r requirements.txt; fi

# Install requirements for fork-jpeg-dna-noise-models
WORKDIR /Codec_Benchmarks/libraries/fork-jpeg-dna-noise-models/v0.2
RUN python3 -m venv venv \
    && . venv/bin/activate \
    && if [ -f requirements.txt ]; then pip3 install -r requirements.txt; fi

# Install requirements for Custom-DNA-Aeon in the specified path
WORKDIR /Codec_Benchmarks/libraries/Custom-DNA-Aeon/libraries/NOREC4DNA
RUN python3 -m venv venv \
    && . venv/bin/activate \
    && if [ -f /Codec_Benchmarks/libraries/Custom-DNA-Aeon/python/NOREC_requirements.txt ]; then pip3 install -r /Codec_Benchmarks/libraries/Custom-DNA-Aeon/python/NOREC_requirements.txt; fi

# Build the C++ binary for Custom-DNA-Aeon
WORKDIR /Codec_Benchmarks/libraries/Custom-DNA-Aeon
RUN mkdir -p build \
    && cd build \
    && cmake .. \
    && make

# Set the working directory back to the main project
WORKDIR /Codec_Benchmarks

# Start a bash shell by default
CMD ["bash"]
