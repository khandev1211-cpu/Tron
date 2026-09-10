# 🚀 Sentinel Sentinel: 24/7 Autonomous VPS Deployment Guide

This guide provides a professional walkthrough for hosting the **Tron Sentinel Control Hub** on a VPS (Ubuntu 24.04). The system is designed for **100% autonomous operation**, meaning it runs 24/7 without requiring manual intervention.

---

## 1. 24/7 Uptime Strategy
The system uses two layers to ensure it never stops:
- **Master Agent Orchestrator:** Constantly monitors sub-agents and restarts them if they fail.
- **Persistence Layer:** Uses `systemd` (Recommended) or `screen` to ensure the process survives SSH disconnections and server reboots.

---

## 2. Server Preparation
Log in to your VPS via SSH and run the following to prepare the environment:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Core Dependencies
sudo apt install -y python3-pip python3-venv redis-server git ufw
```

---

## 3. Live Dashboard Configuration (Firewall)
To allow the client to view the dashboard at `http://<VPS_IP>:8000`, you must open the port:

```bash
# Allow SSH (Crucial: do not lock yourself out!)
sudo ufw allow ssh

# Allow Dashboard Port
sudo ufw allow 8000

# Enable Firewall
sudo ufw enable
```

---

## 4. Deployment Steps

### Clone & Setup
```bash
git clone https://github.com/khandev1211-cpu/Tron.git
cd Tron
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Environment Configuration
Create a `.env` file and add your production API keys and filter ranges.
```bash
nano .env
```

---

## 5. Production Hosting (24/7 Service)
To ensure the system starts automatically on boot and recovers from system crashes, we use a **systemd service**.

### Create Service File
```bash
sudo nano /etc/systemd/system/sentinel.service
```

### Paste following configuration:
```ini
[Unit]
Description=Tron Sentinel Master Agent
After=network.target redis-server.service

[Service]
User=root
WorkingDirectory=/root/Tron
ExecStart=/root/Tron/venv/bin/python3 main.py agent
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Start & Enable Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable sentinel
sudo systemctl start sentinel
```

### Monitor Logs in Real-time
```bash
# View the last 50 lines of logs
journalctl -u sentinel -n 50 -f
```

---

## 6. Client Access & Monitoring
The client can now view the live monitoring system at any time:
👉 **URL**: `http://167.172.140.20:8000`

The system is now a **"Set and Forget"** solution. It will harvest new targets every 6 hours and monitor the blockchain every second, forever.
