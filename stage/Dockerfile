FROM ubuntu:22.04

# Install system packages (NOT Python packages!)
RUN apt-get update && \
    apt-get install -y \
        openssh-server \
        python3 \
        python3-pip \
        nginx \
        curl \
        && rm -rf /var/lib/apt/lists/*

# Create SSH user
RUN useradd -m -s /bin/bash stageuser && \
    echo "stageuser:stagepass" | chpasswd

# Setup SSH
RUN mkdir -p /var/run/sshd
COPY sshd_config /etc/ssh/sshd_config

# Setup NGINX
RUN rm -f /etc/nginx/sites-enabled/default
COPY nginx/default.conf /etc/nginx/sites-enabled/default

# Setup Flask app
COPY flask_app/ /app/
WORKDIR /app

# Create logs directory
RUN mkdir -p /app/logs /var/log/nginx

# Install Python dependencies from requirements.txt
# This includes gunicorn, flask, requests, etc.
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose ports
EXPOSE 22 80 8000


CMD ["/bin/bash", "-c", "service ssh start && service nginx start && gunicorn --config /app/gunicorn.conf.py wsgi:app"]
