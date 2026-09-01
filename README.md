# Docker SSH Project - Week 2

## Overview
This project demonstrates Docker containerization with SSH, NGINX, and Flask.

## Architecture
- **Developer 1**: SSH agent forwarding
- **Developer 2**: Passwordless SSH + port forwarding
- **Jump Server**: Bastion host / SSH gateway
- **Stage Server**: SSH server + NGINX + Flask app

## Quick Start
```bash
docker-compose build
docker-compose up -d
