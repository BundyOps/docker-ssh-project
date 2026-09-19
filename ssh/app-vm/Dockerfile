FROM myubuntu:1.0

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        openssh-server \
        openssh-client && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash dev1 && \
    mkdir -p /home/dev1/.ssh /run/sshd && \
    chown -R dev1:dev1 /home/dev1/.ssh && \
    chmod 700 /home/dev1/.ssh

RUN useradd -m -s /bin/bash jump && \
    mkdir -p /home/jump/.ssh && \
    chown -R jump:jump /home/jump/.ssh && \
    chmod 700 /home/jump/.ssh
    
COPY --chown=dev1:dev1 keys/id_ed25519.pub /home/dev1/.ssh/authorized_keys
RUN chmod 600 /home/dev1/.ssh/authorized_keys

COPY --chown=jump:jump keys/jump.pub /home/jump/.ssh/authorized_keys
RUN chmod 600 /home/jump/.ssh/authorized_keys

RUN printf '\n\
AllowAgentForwarding yes\n\
PubkeyAuthentication yes\n\
AllowTcpForwarding yes\n\
PermitRootLogin no\n' >> /etc/ssh/sshd_config

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D", "-e"]
