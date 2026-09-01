FROM ubuntu:22.04

# Update and install packages
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

# Copy SSH config
COPY sshd_config /etc/ssh/sshd_config

# Copy Flask app (will be added later)
# COPY flask_app/ /app/
# WORKDIR /app
# RUN pip3 install -r requirements.txt

# Copy NGINX config
# COPY nginx/default.conf /etc/nginx/sites-enabled/default

# Expose ports
EXPOSE 22 80 5000

# Start services
CMD ["/bin/bash", "-c", "service ssh start && service nginx start && tail -f /dev/null"]
