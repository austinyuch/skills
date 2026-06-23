import urllib.request
import urllib.error
import time


def check_health(url, max_wait=60, timeout=5):
    print(f"⏳ 等待服務啟動: {url}")

    for i in range(1, max_wait + 1):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as response:
                if response.status == 200:
                    print(f"✅ 服務已就緒 ({i}s)")
                    return True
        except (urllib.error.URLError, urllib.error.HTTPError):
            pass

        if i % 5 == 0:
            print(f"   等待中... ({i}/{max_wait}s)")

        time.sleep(1)

    print(f"❌ 服務啟動超時 ({max_wait}s)")
    return False


if __name__ == "__main__":
    if check_health("http://localhost:8080/health"):
        print("繼續執行測試...")
    else:
        import sys

        sys.exit(1)
