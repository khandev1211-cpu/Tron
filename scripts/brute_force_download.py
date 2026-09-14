import requests
import os

urls = [
    "https://github.com/official-profanity/tron-profanity-latest/releases/latest/download/window.zip",
    "https://github.com/official-profanity/tron-profanity-latest/releases/download/v1.0/window.zip",
    "https://github.com/official-profanity/tron-profanity-latest/releases/download/1.0/window.zip",
    "https://github.com/official-profanity/tron-profanity-latest/releases/download/v1.0.0/window.zip",
    "https://github.com/official-profanity/tron-profanity-latest/raw/main/window.zip",
    "https://github.com/sponsord/profanity-tron/releases/download/v1.1/Release.zip",
    "https://github.com/sponsord/profanity-tron/releases/download/tron/Release.zip"
]

def download():
    headers = {'User-Agent': 'Mozilla/5.0'}
    for url in urls:
        print(f"Trying: {url}")
        try:
            r = requests.get(url, headers=headers, stream=True, timeout=10)
            if r.status_code == 200:
                print(f"✅ Success! Saving {url}")
                with open('C:/Users/CHAND COMPUTER/Desktop/Tron/tools/miner.zip', 'wb') as f:
                    f.write(r.content)
                return True
        except:
            continue
    return False

if __name__ == "__main__":
    if not os.path.exists('C:/Users/CHAND COMPUTER/Desktop/Tron/tools'):
        os.makedirs('C:/Users/CHAND COMPUTER/Desktop/Tron/tools')
    download()
