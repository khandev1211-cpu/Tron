#!/bin/bash

# Sentinel Agent - VPS Miner Auto-Setup (ProVanity Edition)
# Maqsad: ProVanity Linux binary download aur path setup karna.

echo "--- SENTINEL VPS MINER SETUP ---"

# 1. Directory Setup
mkdir -p /root/Tron/tools
cd /root/Tron/tools

# 2. Direct Binary Download (Linux Version)
echo "[*] Downloading ProVanity Linux Binary..."
curl -L -o provanity-linux "https://github.com/WooMai/ProVanity/releases/download/1.1.1/provanity-linux-amd64"

if [ -f "provanity-linux" ]; then
    chmod +x provanity-linux
    MINER_PATH=$(pwd)/provanity-linux
    echo "✅ SUCCESS: ProVanity downloaded at $MINER_PATH"

    # 3. .env File Update
    if [ -f "/root/Tron/.env" ]; then
        echo "[*] Updating .env path..."
        # Escaping path for sed
        sed -i "s|GPU_MINER_PATH=.*|GPU_MINER_PATH=$MINER_PATH|" /root/Tron/.env
        echo "✅ .env updated successfully."
    else
        echo "⚠️ Warning: .env not found at /root/Tron/.env. Set GPU_MINER_PATH manually to: $MINER_PATH"
    fi
else
    echo "❌ ERROR: Download failed. Check your internet connection."
fi

echo "--- SETUP COMPLETE ---"
