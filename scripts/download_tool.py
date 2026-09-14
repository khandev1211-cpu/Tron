import requests
import os

def download_file(url, dest):
    print(f"Downloading {url} to {dest}...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        r = requests.get(url, headers=headers, stream=True)
        r.raise_for_status()
        with open(dest, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        print("✅ Download successful!")
    except Exception as e:
        print(f"❌ Download failed: {e}")

if __name__ == "__main__":
    # Trying the latest release download URL
    url = "https://github.com/official-profanity/tron-profanity-latest/releases/latest/download/window.zip"
    dest = r"C:\Users\CHAND COMPUTER\Desktop\Tron\tools\window.zip"
    if not os.path.exists(os.path.dirname(dest)):
        os.makedirs(os.path.dirname(dest))
    download_file(url, dest)
