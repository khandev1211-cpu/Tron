import requests
import os

def download_provanity():
    url = "https://github.com/WooMai/ProVanity/releases/download/1.1.1/provanity-windows-amd64.exe"
    dest = r"C:\Users\CHAND COMPUTER\Desktop\Tron\tools\provanity.exe"

    if not os.path.exists(os.path.dirname(dest)):
        os.makedirs(os.path.dirname(dest))

    print(f"Downloading ProVanity from: {url}")
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        r = requests.get(url, headers=headers, stream=True, timeout=30)
        r.raise_for_status()
        with open(dest, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024*1024): # 1MB chunks
                if chunk:
                    f.write(chunk)
        print(f"✅ ProVanity downloaded successfully to {dest}")
        return True
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False

if __name__ == "__main__":
    download_provanity()
