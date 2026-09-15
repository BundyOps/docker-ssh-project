FROM docker.arvancloud.ir/ubuntu:26.10

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    curl \
    nano \
    net-tools \
    iputils-ping \
    dnsutils \
    python3-pip \
    python3-venv \
    iproute2 \
    && rm -rf /var/lib/apt/lists/*

# Keep container alive by default
CMD ["sleep", "infinity"]
