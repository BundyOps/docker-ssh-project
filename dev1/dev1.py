#!/usr/bin/env python3

import paramiko
import time
import sys

def ssh_agent_forwarding():
    """Connect to Jump Server using SSH agent forwarding"""
    
    JUMP_HOST = "jump-server"
    JUMP_USER = "jumpuser"
    JUMP_PORT = 22
    
    while True:
        try:
            print(f"[{time.strftime('%H:%M:%S')}] Connecting to Jump Server...")
            
            # Create SSH client
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Connect with agent forwarding enabled
            ssh.connect(
                hostname=JUMP_HOST,
                port=JUMP_PORT,
                username=JUMP_USER,
                allow_agent=True,
                look_for_keys=False
            )
            
            print(f"✅ Connected! SSH agent forwarding active.")
            
            # Keep connection alive
            while True:
                stdin, stdout, stderr = ssh.exec_command("echo 'Connected!'")
                output = stdout.read().decode().strip()
                print(f"   Server says: {output}")
                time.sleep(10)
                
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            print(f"🔄 Retrying in 5 seconds...")
            time.sleep(5)
            continue

if __name__ == "__main__":
    print("🚀 Developer 1: SSH Agent Forwarding Script Started")
    print("====================================================")
    ssh_agent_forwarding()
