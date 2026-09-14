# Sentinel Agent: VPS Setup Guide (Ubuntu 24.04/22.04)

This guide explains how to deploy the Sentinel Agent system on a Linux VPS. The system is designed to automatically detect the lack of a GPU and switch to multi-core CPU mining.

---

## 1. System Requirements & Updates
Login to your VPS via SSH and run:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv redis-server git
```

## 2. Redis Setup
Ensure Redis is running and starts on boot:
```bash
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

## 3. Clone & Environment
```bash
cd /root
git clone <YOUR_GITHUB_REPO_URL>
cd Tron

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 4. Configure `.env`
Create a `.env` file (`nano .env`) and paste your keys:
```env
TRON_GRID_API_KEY=your_key
TRONSCAN_API_KEY=your_key
REDIS_HOST=localhost
REDIS_PORT=6379

# Client Filters
BOT_FILTER_MIN_TRANSFER=200
BOT_FILTER_MAX_TRANSFER=300
BOT_FILTER_MIN_BALANCE=9800
BOT_FILTER_MAX_BALANCE=18500

# GPU Path (On VPS without GPU, this can be empty or dummy)
GPU_MINER_PATH=/usr/bin/provanity-linux
```

## 5. Firewall Configuration
Allow the Dashboard port (8000):
```bash
sudo ufw allow 8000/tcp
sudo ufw enable
```

## 6. Running the System (24/7)
To keep the system running even after you close the SSH window, use `screen`:

```bash
# Start a new screen session
screen -S sentinel

# Activate venv and run
source venv/bin/activate
python3 agent_system.py
```
*   **To Detach**: Press `Ctrl+A` then `D`.
*   **To Re-attach**: Type `screen -r sentinel`.

---

## 7. How it works on VPS
*   **Monitor/Harvester**: Works exactly like on Windows.
*   **GPU Engine**: The system will detect no NVIDIA GPU and automatically launch `scripts/python_miner.py`.
*   **CPU Power**: It will utilize all available CPU cores of your VPS to find matching addresses.
