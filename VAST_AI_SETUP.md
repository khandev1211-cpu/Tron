# Sentinel Agent - Vast.ai Centralized Deployment Guide

This guide describes how to deploy the entire Sentinel Agent system natively inside a Vast.ai container with **2x RTX 4090 GPUs**. Everything runs inside the instance, requiring no external ports or local Windows configurations.

---

## Step 1: Launch Instance on Vast.ai
1. Go to your **Vast.ai Console**.
2. Select a template with **NVIDIA CUDA** or **PyTorch/Nvidia** (Driver version 580+ and CUDA 13 preferred).
3. Allocate an instance with **2x RTX 4090**.
4. Edit the **Edit Image & Ports** button:
   - Ensure port **8000** (Dashboard TCP port) is mapped to be accessible publicly.
5. Launch and connect via SSH once active.

---

## Step 2: Initialize Workspace & Code Base
Inside the Vast.ai instance terminal, execute the following commands:
```bash
# Navigate to the workspace root directory
cd /workspace

# Clone the centralized repository layer
git clone https://github.com/khandev1211-cpu/Tron.git /workspace/Tron
cd /workspace/Tron

# Execute the automated deployment setup sequence
bash scripts/vast_setup.sh
```

---

## Step 3: Run the Local Centralized Database
Start a background Redis server natively inside the instance:
```bash
redis-server --daemonize yes
```
*Verify it is running locally:* `redis-cli ping` should return `PONG`.

---

## Step 4: Environment Settings Configuration
Create a production `.env` configuration file:
```bash
nano /workspace/Tron/.env
```
Paste the following block into the editor, adjusting your precision values:
```env
# --- API CONFIG CORRIDORS ---
TRON_GRID_API_KEY=1a3b90ac-7f2c-4100-83ef-22f8e8585323
TRONSCAN_API_KEY=09e6c62e-dc11-4e6a-88b0-64c70e8d640b

# --- CENTRALIZED STATE LAYER ---
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_TTL=86400

# --- BOT PRODUCTION BALANCES ---
BOT_FILTER_MIN_TRANSFER=200
BOT_FILTER_MAX_TRANSFER=300
BOT_FILTER_MIN_BALANCE=9800
BOT_FILTER_MAX_BALANCE=18500
USDT_CONTRACT=TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t

# --- MULTI-GPU ACTION CONFIG ---
# Path to the provanity executable in your workspace
GPU_MINER_PATH=/workspace/provanity

# Precision level: 3+3 (6 chars total) is optimized for 2-15s matching on 2x 4090
GPU_PREFIX_MATCH_LEN=3
GPU_SUFFIX_MATCH_LEN=3
GPU_MINING_TIMEOUT=15
```
*Save and close:* Press `Ctrl+O`, `Enter`, then `Ctrl+X`.

---

## Step 5: Start the Multi-Agent System (24/7)
Use `screen` to keep the system active continuously after closing the terminal session:

```bash
# Open a persistent console interface slot
screen -S sentinel

# Activate virtual environment
source venv/bin/activate

# Launch the Master Agent Orchestration Hub
python3 agent_system.py
```
- **To Detach (Put in Background)**: Press `Ctrl+A` then `D`.
- **To Re-attach (Check Logs)**: Type `screen -r sentinel`.

---

## Step 6: Opening the Live Control Panel Dashboard
1. Go back to your Vast.ai web dashboard interface.
2. Locate your running instance and look for the **Proxy** buttons, or look under the IP connectivity listings.
3. Click on the link mapped to internal port **8000**.
4. Your responsive Sentinel Hub Dashboard is now accessible from your browser on any phone, laptop, or desktop!
