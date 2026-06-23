#!/usr/bin/env python3
"""
建置開發用 Docker 映像（跨平台模板）

使用方式:
    python build_dev.py
    python build_dev.py --arch arm64
    python build_dev.py --no-cache
"""

import sys
import platform
import subprocess
import argparse
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


# ============ 架構偵測 ============


def detect_arch():
    """偵測系統架構"""
    machine = platform.machine().lower()
    if machine in ("x86_64", "amd64"):
        return "amd64"
    elif machine in ("aarch64", "arm64"):
        return "arm64"
    else:
        return "amd64"


# ============ 命令執行 ============


def run_command(cmd, check=True):
    """執行系統命令"""
    try:
        result = subprocess.run(
            cmd, shell=True, check=check, capture_output=True, text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print_colored(f"❌ 命令執行失敗: {cmd}", Colors.RED)
        print_colored(f"錯誤碼: {e.returncode}", Colors.RED)
        if e.stderr:
            print_colored(f"錯誤訊息:\n{e.stderr}", Colors.RED)
        sys.exit(e.returncode)


# ============ 參數解析 ============


def parse_args():
    """解析命令列參數"""
    parser = argparse.ArgumentParser(description="建置開發用 Docker 映像")
    parser.add_argument(
        "--arch", choices=["amd64", "arm64"], help="目標架構（預設：自動偵測）"
    )
    parser.add_argument("--no-cache", action="store_true", help="不使用 Docker 快取")
    return parser.parse_args()


# ============ 主程式 ============


def main():
    """主程式"""
    # 啟用彩色輸出
    enable_windows_colors()

    # 解析參數
    args = parse_args()

    # 決定架構
    if args.arch:
        arch = args.arch
        print(f"🎯 使用指定架構: {arch}")
    else:
        arch = detect_arch()
        print(f"🔍 自動偵測架構: {arch}")

    # 建置映像
    print_colored("🔨 開始建置映像...", Colors.BLUE)

    cache_flag = "--no-cache" if args.no_cache else ""
    cmd = f"docker build {cache_flag} --build-arg TARGETARCH={arch} -t myapp-dev:{arch} -f Dockerfile.dev ."

    run_command(cmd)

    # 顯示映像資訊
    print_colored("✅ 建置完成！", Colors.GREEN)
    result = run_command(f"docker images myapp-dev:{arch}")
    print(result.stdout)


if __name__ == "__main__":
    main()
