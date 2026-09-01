FROM python:3.9-slim

# Install SSH client
RUN apt-get update && \
    apt-get install -y openssh-client && \
    rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy script
COPY dev2.py .

# Copy SSH key (passwordless authentication)
RUN mkdir -p /root/.ssh
COPY ssh_key/ /root/.ssh/
RUN chmod 600 /root/.ssh/id_rsa
RUN chmod 700 /root/.ssh

# Run the script
CMD ["python", "/app/dev2.py"]
