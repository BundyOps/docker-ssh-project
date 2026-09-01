#!/usr/bin/env python3

import paramiko
import time
import threading
import sys

def passwordless_ssh():
    """Connect to Jump Server using passwordless SSH"""
    
    JUMP_HOST = "jump-server"
    JUMP_USER = "jumpuser"
    JUMP_PORT = 22
    KEY_PATH = "/root/.ssh/id_rsa"
    STAGE_HOST = "stage-server"
    STAGE_PORT = 5000
    
    while True:
        try:
            print(f"[{time.strftime('%H:%M:%S')}] Connecting to Jump Server (passwordless)...")
            
            # Create SSH client
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Connect using SSH key
            ssh.connect(
                hostname=JUMP_HOST,
                port=JUMP_PORT,
                username=JUMP_USER,
                key_filename=KEY_PATH,
                look_for_keys=False
            )
            
            print(f"✅ Connected to Jump Server (passwordless)!")
            print(f"🔗 Creating tunnel to Stage Server...")
            
            # Forward Stage Server API port
            transport = ssh.get_transport()
            channel = transport.open_channel(
                'direct-tcpip',
                ('127.0.0.1', STAGE_PORT),
                (STAGE_HOST, STAGE_PORT)
            )
            
            print(f"✅ Port forwarding active: localhost:{STAGE_PORT} → {STAGE_HOST}:{STAGE_PORT}")
            
            # Keep connection alive
            while True:
                stdin, stdout, stderr = ssh.exec_command("echo 'Connected to Jump Server'")
                output = stdout.read().decode().strip()
                print(f"   Jump Server says: {output}")
                time.sleep(10)
                
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            print(f"🔄 Retrying in 5 seconds...")
            time.sleep(5)
            continue

if __name__ == "__main__":
    print("🚀 Developer 2: Passwordless SSH + Port Forwarding")
    print("====================================================")
    passwordless_ssh()
