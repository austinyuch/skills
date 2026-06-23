#!/usr/bin/env python3
"""
執行 E2E 測試（跨平台模板）

使用方式:
    python e2e_local.py
    python e2e_local.py --skip-build
    python e2e_local.py --keep
"""

import sys
import time
import subprocess
import argparse
import urllib.request
import urllib.error
import re
from pathlib import Path
import ctypes

# ============ 彩色輸出 ============


class Colors:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"


def enable_windows_colors():
    """啟用 Windows 終端彩色輸出"""
    if sys.platform == "win32":
        try:
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass


def print_colored(text, color):
    """彩色輸出"""
    print(f"{color}{text}{Colors.RESET}")


# ============ 命令執行 ============


def run_command(cmd, check=True):
    """執行系統命令"""
    try:
        result = subprocess.run(
            cmd, shell=True, check=check, capture_output=True, text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print_colored(f"❌ 命令執行失敗", Colors.RED)
        if e.stderr:
            print_colored(f"錯誤訊息: {e.stderr}", Colors.RED)
        sys.exit(e.returncode)


def run_with_logging(cmd, log_file):
    """執行命令並即時輸出 + 記錄到檔案"""
    log_file.parent.mkdir(parents=True, exist_ok=True)

    with open(log_file, "w", encoding="utf-8") as f:
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        output_lines = []
        if process.stdout:
            for line in process.stdout:
                print(line, end="")
                f.write(line)
                output_lines.append(line)

        process.wait()

    return process.returncode, "".join(output_lines)


# ============ HTTP Health Check ============


def check_health(url, max_wait=60, timeout=5):
    """等待服務啟動"""
    print(f"⏳ 等待服務啟動: {url}")

    for i in range(1, max_wait + 1):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as response:
                if response.status == 200:
                    print_colored(f"✅ 服務已就緒 ({i}s)", Colors.GREEN)
                    return True
        except (urllib.error.URLError, urllib.error.HTTPError):
            pass

        if i % 5 == 0:
            print(f"   等待中... ({i}/{max_wait}s)")

        time.sleep(1)

    print_colored(f"❌ 服務啟動超時 ({max_wait}s)", Colors.RED)
    return False


# ============ 測試結果解析 ============


def parse_test_results(output):
    """解析測試結果"""
    passed = len(re.findall(r"--- PASS:", output))
    failed = len(re.findall(r"--- FAIL:", output))
    skipped = len(re.findall(r"--- SKIP:", output))
    return passed, failed, skipped


# ============ 架構偵測 ============


def detect_arch():
    """偵測系統架構"""
    import platform

    machine = platform.machine().lower()
    if machine in ("x86_64", "amd64"):
        return "amd64"
    elif machine in ("aarch64", "arm64"):
        return "arm64"
    else:
        return "amd64"


# ============ 主程式 ============


def main():
    """主程式"""
    enable_windows_colors()

    # 解析參數
    parser = argparse.ArgumentParser(description="執行 E2E 測試")
    parser.add_argument("--skip-build", action="store_true", help="跳過建置")
    parser.add_argument("--keep", action="store_true", help="保留容器")
    args = parser.parse_args()

    print("=" * 40)
    print("E2E 測試")
    print("=" * 40)

    # 步驟 1: 建置映像（可選）
    if not args.skip_build:
        print_colored("\n🔨 步驟 1: 建置映像...", Colors.BLUE)
        arch = detect_arch()
        run_command(
            f"docker build --build-arg TARGETARCH={arch} -t myapp-dev:{arch} -f Dockerfile.dev ."
        )
        print_colored("✅ 建置完成", Colors.GREEN)

    # 步驟 2: 啟動容器
    print_colored("\n🚀 步驟 2: 啟動容器...", Colors.BLUE)
    run_command("docker-compose -f docker-compose.dev.yml up -d")

    # 步驟 3: 等待服務就緒
    print_colored("\n⏳ 步驟 3: 等待服務就緒...", Colors.BLUE)
    if not check_health("http://localhost:8080/health"):
        run_command("docker-compose -f docker-compose.dev.yml down")
        sys.exit(1)

    # 步驟 4: 執行測試
    print_colored("\n🧪 步驟 4: 執行測試...", Colors.BLUE)

    log_file = Path("temp") / "e2e-output.log"
    test_cmd = "docker-compose -f docker-compose.dev.yml exec -T app go test -v ./..."

    returncode, output = run_with_logging(test_cmd, log_file)

    # 步驟 5: 解析結果
    print_colored("\n📊 步驟 5: 測試結果...", Colors.BLUE)

    passed, failed, skipped = parse_test_results(output)

    print(f"   通過:  {passed}")
    print(f"   失敗:  {failed}")
    print(f"   跳過:  {skipped}")

    # 步驟 6: 清理
    if not args.keep:
        print_colored("\n🧹 步驟 6: 清理容器...", Colors.BLUE)
        run_command("docker-compose -f docker-compose.dev.yml down")

    # 最終結果
    print("\n" + "=" * 40)
    if failed == 0:
        print_colored("✅ 測試全部通過！", Colors.GREEN)
    else:
        print_colored("❌ 測試失敗", Colors.RED)
        sys.exit(1)
    print("=" * 40)


if __name__ == "__main__":
    main()
