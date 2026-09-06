FROM ubuntu:22.04

# Install SSH server
RUN apt-get update && \
    apt-get install -y openssh-server && \
    rm -rf /var/lib/apt/lists/*

# Create user
RUN useradd -m -s /bin/bash jumpuser && \
    echo "jumpuser:jumppass" | chpasswd

# Create required directories
#docker compose build error if not create this directory
RUN mkdir -p /var/run/sshd && \
    mkdir -p /home/jumpuser/.ssh && \
    chmod 700 /home/jumpuser/.ssh && \
    chown jumpuser:jumpuser /home/jumpuser/.ssh

# Copy SSH config
COPY sshd_config /etc/ssh/sshd_config

# Generate host keys
RUN ssh-keygen -A

# Test SSH config
RUN sshd -t

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]
