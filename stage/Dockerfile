FROM myubuntu:1.0

RUN apt-get update && \
    apt-get install -y --no-install-recommends openssh-server nginx && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash dev && \
    mkdir -p /home/dev/.ssh /run/sshd && \
    chown -R dev:dev /home/dev/.ssh && \
    chmod 700 /home/dev/.ssh

COPY --chown=dev:dev keys/id_ed25519.pub /home/dev/.ssh/authorized_keys

RUN chmod 600 /home/dev/.ssh/authorized_keys

RUN printf '\n\
AllowAgentForwarding yes\n\
PubkeyAuthentication yes\n\
PermitRootLogin no\n' >> /etc/ssh/sshd_config

RUN apt-get update && apt-get install -y --no-install-recommends netcat-openbsd && rm -rf /var/lib/apt/lists/*

EXPOSE 22 80

# Start both nginx and sshd
CMD service nginx start && /usr/sbin/sshd -D -e
