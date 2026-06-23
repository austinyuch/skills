# 跨平台開發工具腳本最佳實踐

> **來源**: Task 8.8 - 本地開發 Docker 環境 Python 跨平台版本實作經驗  
> **日期**: 2026-02-05  
> **適用場景**: 開發輔助腳本、自動化工具、CI/CD 腳本

---

## 核心原則

### 優先使用 Python 而非 Bash

**原因**:
- ✅ **真正跨平台**: Windows/macOS/Linux 原生支援，無需 WSL/Git Bash
- ✅ **無外部依賴**: Python 3.7+ 標準庫即可實現大部分功能
- ✅ **更好的錯誤處理**: try/except 提供精細的錯誤控制
- ✅ **更清晰的程式碼**: Python 可讀性和可維護性更高
- ✅ **優雅降級**: 舊系統可以降級功能而不報錯

**Bash 的局限性**:
- ❌ Windows 需要 WSL/Git Bash/Cygwin
- ❌ 路徑處理在 Windows 上容易出錯
- ❌ 彩色輸出在 Windows 上不穩定
- ❌ 錯誤處理較為粗糙（`set -e` 全域性）

---

## Python 跨平台實作模式

### 1. 架構偵測

**問題**: 不同平台回傳不同的架構名稱

**解決方案**: 使用 `platform.machine()` 統一處理

```python
import platform

def detect_arch():
    """偵測系統架構，回傳統一格式"""
    machine = platform.machine().lower()
    if machine in ('x86_64', 'amd64'):
        return 'amd64'
    elif machine in ('aarch64', 'arm64'):
        return 'arm64'
    else:
        return 'amd64'  # 預設值
```

**平台對應**:
| 平台 | platform.machine() | 統一輸出 |
|------|-------------------|----------|
| Windows x64 | AMD64 | amd64 |
| Windows ARM | ARM64 | arm64 |
| macOS Intel | x86_64 | amd64 |
| macOS Apple Silicon | arm64 | arm64 |
| Linux x64 | x86_64 | amd64 |
| Linux ARM | aarch64 | arm64 |

---

### 2. 彩色輸出

**問題**: Windows 終端預設不支援 ANSI 色碼

**解決方案**: 啟用 Windows Virtual Terminal Processing

```python
import sys
import ctypes

def enable_windows_colors():
    """啟用 Windows 終端彩色輸出"""
    if sys.platform == 'win32':
        try:
            kernel32 = ctypes.windll.kernel32
            # 啟用 Virtual Terminal Processing (VT100)
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            # 優雅降級：舊版 Windows 不報錯
            pass

# ANSI 色碼定義
class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'

def print_colored(text, color):
    """彩色輸出（跨平台）"""
    print(f"{color}{text}{Colors.RESET}")

# 使用範例
enable_windows_colors()  # 腳本開頭呼叫一次
print_colored("✅ 成功", Colors.GREEN)
print_colored("❌ 錯誤", Colors.RED)
```

**優雅降級**:
- Windows 10+: ✅ 彩色輸出
- Windows 7/8: ⚠️ 無色輸出（不會報錯）
- macOS/Linux: ✅ 彩色輸出

---

### 3. 路徑處理

**問題**: Windows 使用反斜線 `\`，Unix 使用斜線 `/`

**解決方案**: 使用 `pathlib.Path`

```python
from pathlib import Path

# 跨平台路徑操作
output_dir = Path("temp")
output_dir.mkdir(exist_ok=True)

# 路徑拼接（自動處理分隔符）
log_file = output_dir / "output.log"
config_file = output_dir / "config.json"

# 讀取檔案
with open(log_file, 'w') as f:
    f.write("Log content")

# 檢查檔案存在
if log_file.exists():
    print(f"Log file: {log_file}")
```

**優勢**:
- 自動處理 Windows `\` 和 Unix `/`
- 跨平台路徑拼接
- 更安全的檔案操作

---

### 4. 命令執行

**問題**: 需要跨平台執行系統命令

**解決方案**: 使用 `subprocess` 模組

```python
import subprocess
import sys

def run_command(cmd, check=True, capture_output=True):
    """
    執行系統命令（跨平台）
    
    Args:
        cmd: 命令字串
        check: 是否檢查返回碼（預設 True）
        capture_output: 是否捕獲輸出（預設 True）
    
    Returns:
        subprocess.CompletedProcess 物件
    """
    try:
        result = subprocess.run(
            cmd,
            shell=True,  # Windows 用 cmd.exe，Unix 用 /bin/sh
            check=check,
            capture_output=capture_output,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print_colored(f"❌ 命令執行失敗: {cmd}", Colors.RED)
        print_colored(f"錯誤碼: {e.returncode}", Colors.RED)
        if e.stderr:
            print_colored(f"錯誤訊息:\n{e.stderr}", Colors.RED)
        sys.exit(e.returncode)

# 使用範例
result = run_command("docker --version")
print(result.stdout)

# 不檢查返回碼的範例
result = run_command("docker ps", check=False)
if result.returncode != 0:
    print("Docker 未啟動")
```

**跨平台行為**:
- Windows: 使用 `cmd.exe`
- macOS/Linux: 使用 `/bin/sh`
- 統一的錯誤處理

---

### 5. HTTP 請求

**問題**: 需要檢查服務健康狀態（HTTP health check）

**解決方案**: 使用 `urllib.request`（標準庫，無需安裝）

```python
import urllib.request
import urllib.error
import time

def check_health(url, max_wait=60, timeout=5):
    """
    等待服務啟動（HTTP health check）
    
    Args:
        url: 健康檢查 URL
        max_wait: 最大等待時間（秒）
        timeout: 單次請求超時（秒）
    
    Returns:
        bool: 服務是否就緒
    """
    print(f"⏳ 等待服務啟動: {url}")
    
    for i in range(1, max_wait + 1):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as response:
                if response.status == 200:
                    print_colored(f"✅ 服務已就緒 ({i}s)", Colors.GREEN)
                    return True
        except (urllib.error.URLError, urllib.error.HTTPError):
            pass
        
        # 每 5 秒顯示進度
        if i % 5 == 0:
            print(f"   等待中... ({i}/{max_wait}s)")
        
        time.sleep(1)
    
    print_colored(f"❌ 服務啟動超時 ({max_wait}s)", Colors.RED)
    return False

# 使用範例
if check_health("http://localhost:8080/health"):
    print("繼續執行測試...")
else:
    sys.exit(1)
```

**優勢**:
- Python 標準庫（無外部依賴）
- 跨平台支援
- 簡單可靠

---

### 6. 參數解析

**問題**: 需要處理命令列參數

**解決方案**: 使用 `argparse` 模組

```python
import argparse

def parse_args():
    """解析命令列參數"""
    parser = argparse.ArgumentParser(
        description='建置開發用 Docker 映像',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用範例:
  python build_dev.py                 # 自動偵測架構
  python build_dev.py --arch arm64    # 指定架構
  python build_dev.py --no-cache      # 無快取建置
        '''
    )
    
    parser.add_argument(
        '--arch',
        choices=['amd64', 'arm64'],
        help='目標架構（預設：自動偵測）'
    )
    
    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='不使用 Docker 快取'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='顯示詳細輸出'
    )
    
    return parser.parse_args()

# 使用範例
args = parse_args()

if args.arch:
    arch = args.arch
else:
    arch = detect_arch()

cache_flag = '--no-cache' if args.no_cache else ''
```

**優勢**:
- 自動生成 `--help` 訊息
- 標準化的參數處理
- 自動驗證參數值

---

### 7. 即時輸出 + 檔案記錄

**問題**: 需要同時在終端顯示輸出並記錄到檔案

**解決方案**: 使用 `subprocess.Popen` + 行緩衝

```python
import subprocess
from pathlib import Path

def run_with_logging(cmd, log_file):
    """
    執行命令並即時輸出 + 記錄到檔案
    
    Args:
        cmd: 命令字串
        log_file: 日誌檔案路徑（Path 物件）
    """
    print(f"📝 執行: {cmd}")
    print(f"📁 日誌: {log_file}")
    
    # 確保日誌目錄存在
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 開始執行並記錄
    with open(log_file, 'w', encoding='utf-8') as f:
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1  # 行緩衝
        )
        
        # 即時輸出每一行
        for line in process.stdout:
            print(line, end='')  # 終端顯示
            f.write(line)        # 檔案記錄
        
        process.wait()
    
    # 檢查返回碼
    if process.returncode != 0:
        print_colored(f"❌ 命令失敗 (返回碼: {process.returncode})", Colors.RED)
        sys.exit(process.returncode)
    
    print_colored("✅ 命令執行成功", Colors.GREEN)

# 使用範例
log_file = Path("temp") / "test-output.log"
run_with_logging("go test -v ./...", log_file)
```

**優勢**:
- 使用者可即時看到進度
- 完整記錄保存到檔案
- 不需要 `tee` 命令（跨平台）

---

### 8. 正則表達式解析輸出

**問題**: 需要從命令輸出中提取結構化資訊

**解決方案**: 使用 `re` 模組

```python
import re

def parse_test_results(output):
    """
    解析測試結果
    
    Args:
        output: 測試輸出字串
    
    Returns:
        tuple: (passed, failed, skipped)
    """
    # 統計測試結果
    passed = len(re.findall(r'--- PASS:', output))
    failed = len(re.findall(r'--- FAIL:', output))
    skipped = len(re.findall(r'--- SKIP:', output))
    
    return passed, failed, skipped

# 使用範例
with open("temp/test-output.log", 'r') as f:
    output = f.read()

passed, failed, skipped = parse_test_results(output)

print(f"📊 測試結果:")
print(f"   通過:  {passed}")
print(f"   失敗:  {failed}")
print(f"   跳過:  {skipped}")

if failed > 0:
    print_colored("❌ 測試失敗", Colors.RED)
    sys.exit(1)
```

---

## 完整範例：建置腳本

```python
#!/usr/bin/env python3
"""
建置開發用 Docker 映像（跨平台）

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
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'

def enable_windows_colors():
    """啟用 Windows 終端彩色輸出"""
    if sys.platform == 'win32':
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
    if machine in ('x86_64', 'amd64'):
        return 'amd64'
    elif machine in ('aarch64', 'arm64'):
        return 'arm64'
    else:
        return 'amd64'

# ============ 命令執行 ============

def run_command(cmd, check=True):
    """執行系統命令"""
    try:
        result = subprocess.run(
            cmd, shell=True, check=check,
            capture_output=True, text=True
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
    parser = argparse.ArgumentParser(description='建置開發用 Docker 映像')
    parser.add_argument('--arch', choices=['amd64', 'arm64'], 
                       help='目標架構（預設：自動偵測）')
    parser.add_argument('--no-cache', action='store_true',
                       help='不使用 Docker 快取')
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
    
    cache_flag = '--no-cache' if args.no_cache else ''
    cmd = f'docker build {cache_flag} --build-arg TARGETARCH={arch} -t myapp-dev:{arch} -f Dockerfile.dev .'
    
    run_command(cmd)
    
    # 顯示映像資訊
    print_colored("✅ 建置完成！", Colors.GREEN)
    result = run_command(f'docker images myapp-dev:{arch}')
    print(result.stdout)

if __name__ == '__main__':
    main()
```

---

## 完整範例：E2E 測試腳本

```python
#!/usr/bin/env python3
"""
執行 E2E 測試（跨平台）

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

# [此處包含上面定義的 Colors, enable_windows_colors, print_colored 等函數]

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
    passed = len(re.findall(r'--- PASS:', output))
    failed = len(re.findall(r'--- FAIL:', output))
    skipped = len(re.findall(r'--- SKIP:', output))
    return passed, failed, skipped

# ============ 主程式 ============

def main():
    """主程式"""
    enable_windows_colors()
    
    # 解析參數
    parser = argparse.ArgumentParser(description='執行 E2E 測試')
    parser.add_argument('--skip-build', action='store_true', help='跳過建置')
    parser.add_argument('--keep', action='store_true', help='保留容器')
    args = parser.parse_args()
    
    print("=" * 40)
    print("E2E 測試")
    print("=" * 40)
    
    # 步驟 1: 建置映像（可選）
    if not args.skip_build:
        print_colored("\n🔨 步驟 1: 建置映像...", Colors.BLUE)
        arch = detect_arch()
        run_command(f'docker build --build-arg TARGETARCH={arch} -t myapp-dev:{arch} -f Dockerfile.dev .')
        print_colored("✅ 建置完成", Colors.GREEN)
    
    # 步驟 2: 啟動容器
    print_colored("\n🚀 步驟 2: 啟動容器...", Colors.BLUE)
    run_command('docker-compose -f docker-compose.dev.yml up -d')
    
    # 步驟 3: 等待服務就緒
    print_colored("\n⏳ 步驟 3: 等待服務就緒...", Colors.BLUE)
    if not check_health("http://localhost:8080/health"):
        run_command('docker-compose -f docker-compose.dev.yml down')
        sys.exit(1)
    
    # 步驟 4: 執行測試
    print_colored("\n🧪 步驟 4: 執行測試...", Colors.BLUE)
    
    log_file = Path("temp") / "e2e-output.log"
    log_file.parent.mkdir(exist_ok=True)
    
    # 執行測試並記錄
    test_cmd = 'docker-compose -f docker-compose.dev.yml exec -T app go test -v ./...'
    
    with open(log_file, 'w') as f:
        process = subprocess.Popen(
            test_cmd, shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True, bufsize=1
        )
        
        output_lines = []
        for line in process.stdout:
            print(line, end='')
            f.write(line)
            output_lines.append(line)
        
        process.wait()
    
    # 步驟 5: 解析結果
    print_colored("\n📊 步驟 5: 測試結果...", Colors.BLUE)
    
    output = ''.join(output_lines)
    passed, failed, skipped = parse_test_results(output)
    
    print(f"   通過:  {passed}")
    print(f"   失敗:  {failed}")
    print(f"   跳過:  {skipped}")
    
    # 步驟 6: 清理
    if not args.keep:
        print_colored("\n🧹 步驟 6: 清理容器...", Colors.BLUE)
        run_command('docker-compose -f docker-compose.dev.yml down')
    
    # 最終結果
    print("\n" + "=" * 40)
    if failed == 0:
        print_colored("✅ 測試全部通過！", Colors.GREEN)
    else:
        print_colored("❌ 測試失敗", Colors.RED)
        sys.exit(1)
    print("=" * 40)

if __name__ == '__main__':
    main()
```

---

## 檔案命名規範

**Python 腳本命名**:
- 使用 `snake_case` 格式
- 範例: `build_dev.py`, `e2e_local.py`, `deploy_prod.py`

**Bash 腳本命名**（如果必須使用）:
- 使用 `kebab-case` 格式
- 範例: `build-dev.sh`, `e2e-local.sh`, `deploy-prod.sh`

---

## 遷移檢查清單

從 Bash 遷移到 Python 時，確認以下項目：

### 功能對等性
- [ ] 所有命令列參數都已實作
- [ ] 所有錯誤處理邏輯都已遷移
- [ ] 所有輸出訊息都已保留
- [ ] 功能完全相同，無遺漏

### 跨平台測試
- [ ] Windows 10/11 測試通過
- [ ] macOS (Intel + Apple Silicon) 測試通過
- [ ] Linux (AMD64 + ARM64) 測試通過
- [ ] 彩色輸出在所有平台正常

### 文件更新
- [ ] README.md 更新腳本引用
- [ ] 文檔中的使用範例更新
- [ ] CI/CD 配置更新
- [ ] 開發者指南更新

### 移除舊腳本
- [ ] 備份舊的 Bash 腳本（如需要）
- [ ] 刪除舊的 `.sh` 檔案
- [ ] 確認沒有遺留的引用

---

## 經驗教訓

### 成功經驗

1. **Python 標準庫足夠強大**: 無需外部依賴即可實現所有功能
2. **跨平台測試重要**: 在 Windows/macOS/Linux 上都測試通過
3. **保持功能對等**: 與 Bash 版本功能完全對等，降低遷移風險
4. **優雅降級**: Windows 舊版本無色輸出但不報錯

### 改進空間

1. **Python 版本檢查**: 可新增 Python 3.7+ 版本檢查
2. **進度顯示**: 可新增更友善的進度條
3. **配置檔案**: 可支援外部配置檔案

---

## 參考資源

### Python 標準庫文件
- [subprocess](https://docs.python.org/3/library/subprocess.html) - 命令執行
- [argparse](https://docs.python.org/3/library/argparse.html) - 參數解析
- [platform](https://docs.python.org/3/library/platform.html) - 系統資訊
- [pathlib](https://docs.python.org/3/library/pathlib.html) - 路徑處理
- [urllib.request](https://docs.python.org/3/library/urllib.request.html) - HTTP 請求
- [re](https://docs.python.org/3/library/re.html) - 正則表達式

### Windows 終端支援
- [Windows Console Virtual Terminal Sequences](https://docs.microsoft.com/en-us/windows/console/console-virtual-terminal-sequences)
- [SetConsoleMode function](https://docs.microsoft.com/en-us/windows/console/setconsolemode)

---

**最後更新**: 2026-02-05  
**適用版本**: Python 3.7+
