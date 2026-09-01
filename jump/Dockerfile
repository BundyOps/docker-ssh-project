FROM ubuntu:22.04

# Install SSH server
RUN apt-get update && \
    apt-get install -y openssh-server && \
    rm -rf /var/lib/apt/lists/*

# Create SSH user
RUN useradd -m -s /bin/bash jumpuser && \
    echo "jumpuser:jumppass" | chpasswd

# Copy SSH config
COPY sshd_config /etc/ssh/sshd_config

# Allow SSH agent forwarding
RUN echo "AllowAgentForwarding yes" >> /etc/ssh/sshd_config

# Expose SSH port
EXPOSE 22

# Start SSH
CMD ["/usr/sbin/sshd", "-D"]
