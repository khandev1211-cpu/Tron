# VPS Access Guide

## SSH Access Details
- **Command**: `ssh root@167.172.140.20`
- **User**: `root`
- **Password**: `Golden7River`

## How to Connect from Windows:
1. Open **PowerShell** or **Command Prompt**.
2. Type `ssh root@167.172.140.20` and press Enter.
3. If it asks "Are you sure you want to continue connecting?", type `yes` and press Enter.
4. When asked for password, type `Golden7River` (you won't see characters while typing).
5. Press Enter to log in.

## Deployment Commands (Ubuntu 24.04):

### 1. Update & Install Dependencies
```bash
apt update && apt upgrade -y
apt install -y python3-pip python3-venv redis-server git
```

### 2. Configure Redis
```bash
systemctl enable redis-server
systemctl start redis-server
# Verify with: redis-cli ping
```

### 3. Setup Project
```bash
cd /root
git clone https://github.com/khandev1211-cpu/Tron.git
cd Tron
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Create Environment File
```bash
nano .env
# Paste your .env content here
```

### 5. Run Sentinel Agent
```bash
python3 main.py agent
```
