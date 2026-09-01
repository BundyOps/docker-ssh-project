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
COPY dev1.py .

# Create SSH directory
RUN mkdir -p /root/.ssh

# Run the script
CMD ["python", "/app/dev1.py"]
