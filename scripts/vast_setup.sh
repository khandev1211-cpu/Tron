#!/bin/bash

# Sentinel Agent - Vast.ai Dual RTX 4090 Provisioning Script
# This script sets up python dependencies and prepares the workspace inside the Vast.ai container.

echo "=================================================="
echo "    SENTINEL AGENT - VAST.AI PROVISIONING         "
echo "=================================================="

# 1. Update and install basic tools
echo "[*] Installing Python environment packages..."
apt-get update && apt-get install -y python3-pip python3-venv curl git redis-tools

# 2. Setup Virtual Environment
echo "[*] Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 3. Install required Python packages
echo "[*] Installing dependencies..."
pip install redis python-dotenv

# 4. Verify GPU visibility
echo "[*] Verifying NVIDIA Driver and CUDA context..."
if command -v nvidia-smi &> /dev/null
then
    nvidia-smi
    echo "✅ GPUs are perfectly visible to the container environment."
else
    echo "❌ WARNING: nvidia-smi not found. Ensure this instance has GPU support."
fi

echo "=================================================="
echo " SETUP MUKAMMAL: Please configure your .env file "
echo " pointing to your local Ngrok tunnel address.     "
echo "=================================================="
