FROM docker.arvancloud.ir/ubuntu:26.10

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y \
    python3-pip \
    python3-venv \
    iputils-ping \
    iproute2 \
    curl

WORKDIR /home/ubuntu/project

# 1. Only the dependency manifest first — this layer rarely changes
COPY deploy/requirements.txt .

# 2. Install deps — cached unless requirements.txt changes
RUN python3 -m venv . && \
    . bin/activate && \
    pip install --no-cache-dir -r requirements.txt

# 3. Now copy the rest of the project — changes here don't touch pip layer
COPY src .

RUN mkdir -p logs

EXPOSE 8000

CMD ["/bin/bash", "-c", "source bin/activate && gunicorn --config gunicorn.conf.py wsgi:app"]
