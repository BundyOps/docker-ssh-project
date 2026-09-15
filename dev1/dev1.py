#!/usr/bin/env python3

"""
Developer 1: SSH Agent Forwarding Script

This script connects to Jump Server using SSH agent forwarding.
It keeps trying if the connection fails or gets disconnected.
"""

import paramiko
import time
import sys
import os
import socket
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


class SSHForwardingClient:
    """SSH client with agent forwarding and auto-reconnect"""
    
    def __init__(self):
        # Connection settings
        self.jump_host = "jump-server"
        self.jump_user = "jumpuser"
        self.jump_port = 22
        
        # Stage server for testing
        self.stage_host = "stage-server"
        self.stage_user = "stageuser"
        self.stage_port = 22
        
        # Retry settings
        self.retry_delay = 5  # seconds
        self.keepalive_interval = 30  # seconds
        
        # SSH client
        self.ssh = None
        self.transport = None
        
    def connect(self):
        """Connect to Jump Server with agent forwarding"""
        try:
            logger.info(f"Connecting to {self.jump_user}@{self.jump_host}:{self.jump_port}...")
            
            # Create SSH client
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Connect with agent forwarding enabled
            self.ssh.connect(
                hostname=self.jump_host,
                port=self.jump_port,
                username=self.jump_user,
                allow_agent=True,           # Enable SSH agent
                look_for_keys=False,        # Don't look for local keys
                timeout=10,
                compress=True
            )
            
            # Get transport for keepalive
            self.transport = self.ssh.get_transport()
            if self.transport:
                self.transport.set_keepalive(self.keepalive_interval)
            
            logger.info(f"✅ Connected to Jump Server!")
            logger.info(f"   SSH agent forwarding is ACTIVE")
            
            return True
            
        except paramiko.AuthenticationException:
            logger.error("❌ Authentication failed! Check if your key is in the SSH agent.")
            logger.error("   On host, run: ssh-add ~/.ssh/id_rsa_jump")
            return False
            
        except paramiko.SSHException as e:
            logger.error(f"❌ SSH error: {e}")
            return False
            
        except socket.error as e:
            logger.error(f"❌ Socket error: {e}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Connection error: {e}")
            return False
    
    def test_stage_server(self):
        """Test connection to Stage Server through Jump Server"""
        try:
            logger.info("   Testing connection to Stage Server...")
            
            # Execute command through Jump Server
            command = f"ssh -o StrictHostKeyChecking=no {self.stage_user}@{self.stage_host} 'echo Connected to Stage Server!'"
            stdin, stdout, stderr = self.ssh.exec_command(command)
            
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()
            
            if "Connected to Stage Server!" in output:
                logger.info(f"   ✅ Stage Server: {output}")
                return True
            else:
                logger.warning(f"   ⚠️ Stage Server test failed: {error or 'No response'}")
                return False
                
        except Exception as e:
            logger.warning(f"   ⚠️ Could not reach Stage Server: {e}")
            return False
    
    def send_keepalive(self):
        """Send keepalive command to keep connection alive"""
        try:
            stdin, stdout, stderr = self.ssh.exec_command("echo 'Keepalive'")
            output = stdout.read().decode().strip()
            logger.info(f"   Server says: {output}")
            return True
        except Exception as e:
            logger.warning(f"   Keepalive failed: {e}")
            return False
    
    def run(self):
        """Main loop - keeps connection alive with retries"""
        logger.info("🚀 Developer 1: SSH Agent Forwarding Script")
        logger.info("=" * 50)
        logger.info(f"   Jump Server: {self.jump_user}@{self.jump_host}:{self.jump_port}")
        logger.info("   Agent forwarding: ENABLED")
        logger.info("   Auto-reconnect: YES")
        logger.info("=" * 50)
        
        while True:
            # Try to connect
            if not self.connect():
                logger.info(f"🔄 Retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
                continue
            
            # Test connection to Stage Server
            self.test_stage_server()
            
            # Keep connection alive
            logger.info("📡 Connection established. Monitoring...")
            while True:
                try:
                    # Send keepalive every interval
                    if not self.send_keepalive():
                        # Connection lost, break inner loop to reconnect
                        break
                    
                    # Wait for next interval
                    time.sleep(self.keepalive_interval)
                    
                except KeyboardInterrupt:
                    raise
                    
                except Exception as e:
                    logger.warning(f"Connection error: {e}")
                    break  # Break inner loop to reconnect
            
            # Cleanup old connection
            try:
                if self.ssh:
                    self.ssh.close()
            except:
                pass
            
            logger.info("🔄 Connection lost. Reconnecting...")
            time.sleep(self.retry_delay)


def main():
    """Entry point"""
    try:
        client = SSHForwardingClient()
        client.run()
    except KeyboardInterrupt:
        logger.info("\n🛑 Script stopped by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
