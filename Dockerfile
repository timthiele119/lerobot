FROM nvidia/cuda:12.8.0-devel-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 python3.10-venv python3.10-dev python3-pip \
    git curl ca-certificates \
    build-essential pkg-config \
    ffmpeg \
    libffi-dev libudev-dev \
    cmake ninja-build \
    libglib2.0-0 libgl1 \
    libegl1-mesa-dev libgl1-mesa-dev mesa-common-dev \
    libx11-dev libxext-dev libxrender-dev libsm6 \
    && rm -rf /var/lib/apt/lists/*

# venv
RUN python3.10 -m venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH

RUN pip install -U pip wheel setuptools

# PyTorch CUDA 12.8 (known good)
RUN pip install torch==2.7.1 torchvision==0.22.1 \
  --index-url https://download.pytorch.org/whl/cu128

WORKDIR /workspace
COPY . /workspace

# lerobot + all extras + feetech
RUN pip install -e ".[all,feetech]"

CMD ["python", "-c", "import torch, lerobot; print('OK', torch.cuda.get_device_name(0))"]