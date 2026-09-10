# 🗄️ Redis Data Persistence Setup (VPS)

This document details the configuration of the Redis server on the VPS to ensure zero data loss and high-speed pattern matching.

## 1. Installation
```bash
sudo apt update
sudo apt install redis-server -y
```

## 2. Service Management
Ensures Redis starts automatically on system boot.
```bash
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

## 3. Security Configuration
Default settings are optimized for local agent communication:
- **Binding**: `127.0.0.1` (Only local processes can access).
- **Protected Mode**: `yes`.
- **Persistence**: Snapshotting (RDB) is enabled by default to save data to disk every few minutes.

## 4. Troubleshooting
If the Sentinel Agent reports "Redis Down", run:
```bash
# Check if service is active
sudo systemctl status redis-server

# Test connection
redis-cli ping
```

## 5. Cleaning Data (Optional)
To clear all harvested targets and matches:
```bash
redis-cli flushall
```
