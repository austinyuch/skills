---
name: cross-platform-dev-scripts
description: 跨平台開發輔助腳本最佳實踐指南。當需要創建開發輔助工具、自動化腳本、CI/CD 腳本時使用，特別是需要在 Windows/macOS/Linux 跨平台運行的場景。包含 Python 腳本模板、架構偵測、彩色輸出、HTTP health check、命令執行、測試結果解析等實用模式。適用場景：(1) Docker 建置腳本，(2) E2E 測試腳本，(3) 部署自動化腳本，(4) 任何需要跨平台執行的開發工具腳本。
---

# 跨平台開發腳本

## 概述

此 skill 提供創建跨平台開發輔助腳本的最佳實踐，幫助你使用 Python 建立真正跨平台的自動化工具（Windows/macOS/Linux）。

**核心理念**: 優先使用 Python 而非 Bash，實現真正的跨平台支援。

## 何時使用此 Skill

當你需要創建以下類型的腳本時：

- 🔨 Docker 映像建置腳本
- 🧪 E2E 測試自動化腳本
- 🚀 部署和發布腳本
- 🛠️ 開發環境設定腳本
- 📦 打包和發佈工具

**關鍵觸發詞**：「跨平台」、「Windows 支援」、「建置腳本」、「測試腳本」、「自動化」

## 核心原則

### 為什麼選擇 Python 而非 Bash？

| 特性             | Bash                 | Python              |
| ---------------- | -------------------- | ------------------- |
| **Windows 支援** | ❌ 需要 WSL/Git Bash | ✅ 原生支援         |
| **路徑處理**     | ❌ 容易出錯          | ✅ pathlib 自動處理 |
| **彩色輸出**     | ❌ Windows 不穩定    | ✅ VT Processing    |
| **錯誤處理**     | ❌ `set -e` 粗糙     | ✅ try/except 精細  |
| **可維護性**     | ⚠️ 中等              | ✅ 更清晰           |
| **外部依賴**     | ⚠️ 依賴系統工具      | ✅ 標準庫足夠       |

### 設計目標

1. **無外部依賴**：僅使用 Python 3.7+ 標準庫
2. **優雅降級**：舊系統降級功能而不報錯
3. **即時反饋**：彩色輸出 + 即時進度顯示
4. **完整記錄**：同時輸出到終端和檔案

## 快速開始

### 基本腳本結構

```python
#!/usr/bin/env python3
"""腳本說明"""

import sys
import subprocess
from pathlib import Path

def main():
    """主程式"""
    print("開始執行...")
    # 你的程式碼

if __name__ == '__main__':
    main()
```

### 常用模組

```python
import sys           # 系統操作（exit, platform）
import subprocess    # 命令執行
import argparse      # 參數解析
import platform      # 系統資訊（架構偵測）
import urllib.request # HTTP 請求
from pathlib import Path  # 跨平台路徑處理
import re            # 正則表達式（解析輸出）
```

## 核心功能模式

### 1. 架構偵測

自動偵測系統架構（AMD64/ARM64）：

```python
import platform

def detect_arch():
    machine = platform.machine().lower()
    if machine in ('x86_64', 'amd64'):
        return 'amd64'
    elif machine in ('aarch64', 'arm64'):
        return 'arm64'
    else:
        return 'amd64'  # 預設值
```

**適用場景**：Docker 建置、平台特定操作

### 2. 彩色輸出（Windows 支援）

參考 [scripts/colorized_output.py](scripts/colorized_output.py) 以查看完整的彩色輸出實作。

**適用場景**：所有需要使用者互動的腳本

### 3. 跨平台路徑處理

```python
from pathlib import Path

# 自動處理 Windows \ 和 Unix /
output_dir = Path("temp")
output_dir.mkdir(exist_ok=True)

log_file = output_dir / "output.log"
config_file = output_dir / "config.json"

# 檢查檔案
if log_file.exists():
    print(f"日誌檔案: {log_file}")
```

**適用場景**：所有涉及檔案操作的腳本

### 4. 命令執行與錯誤處理

參考 [scripts/command_execution.py](scripts/command_execution.py) 以查看健壯的命令執行模式。

**適用場景**：Docker、Git、測試命令執行

### 5. HTTP Health Check

參考 [scripts/http_health_check.py](scripts/http_health_check.py) 以查看 HTTP health check 實作。

**適用場景**：E2E 測試、部署驗證

### 6. 即時輸出 + 檔案記錄

參考 [scripts/realtime_logging.py](scripts/realtime_logging.py) 以查看即時輸出與記錄實作。

**適用場景**：長時間執行的測試、建置過程

### 7. 測試結果解析

```python
import re

def parse_test_results(output):
    passed = len(re.findall(r'--- PASS:', output))
    failed = len(re.findall(r'--- FAIL:', output))
    skipped = len(re.findall(r'--- SKIP:', output))
    return passed, failed, skipped
```

**適用場景**：測試自動化、CI/CD 管道

### 8. 命令列參數解析

```python
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='建置開發映像')

    parser.add_argument('--arch', choices=['amd64', 'arm64'],
                       help='目標架構（預設：自動偵測）')

    parser.add_argument('--no-cache', action='store_true',
                       help='不使用快取')

    parser.add_argument('--verbose', '-v', action='store_true',
                       help='顯示詳細輸出')

    return parser.parse_args()
```

**適用場景**：所有需要參數的腳本

## 完整範例

### 範例 1: Docker 建置腳本

參考 [scripts/build_dev_template.py](scripts/build_dev_template.py) 以查看完整的 Docker 建置腳本範例。

**功能**：

- ✅ 自動架構偵測
- ✅ 彩色輸出（Windows 支援）
- ✅ 參數解析（--arch, --no-cache）
- ✅ 錯誤處理
- ✅ 映像資訊顯示

**使用方式**：

```bash
python build_dev.py                 # 自動偵測
python build_dev.py --arch arm64    # 指定架構
python build_dev.py --no-cache      # 無快取建置
```

### 範例 2: E2E 測試腳本

參考 [scripts/e2e_test_template.py](scripts/e2e_test_template.py) 以查看完整的 E2E 測試腳本範例。

**功能**：

- ✅ 完整測試流程（建置 → 啟動 → 等待 → 測試 → 清理）
- ✅ HTTP health check
- ✅ 即時輸出 + 檔案記錄
- ✅ 測試結果解析
- ✅ 參數支援（--skip-build, --keep）

**使用方式**：

```bash
python e2e_local.py                 # 完整流程
python e2e_local.py --skip-build    # 跳過建置
python e2e_local.py --keep          # 保留容器
```

## 遷移檢查清單

從 Bash 遷移到 Python 時，請確認：

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

## 最佳實踐

### 檔案命名

**Python 腳本**：使用 `snake_case`

```
build_dev.py
e2e_local.py
deploy_prod.py
```

**Bash 腳本**（如果必須）：使用 `kebab-case`

```
build-dev.sh
e2e-local.sh
deploy-prod.sh
```

### 錯誤處理策略

```python
try:
    result = subprocess.run(cmd, check=True)
except subprocess.CalledProcessError as e:
    print_colored(f"❌ 錯誤: {e}", Colors.RED)
    sys.exit(e.returncode)
```

### 進度顯示

```python
for i in range(1, max_wait + 1):
    if i % 5 == 0:
        print(f"⏳ 等待中... ({i}/{max_wait}s)")
    time.sleep(1)
```

### Python 版本檢查

```python
import sys

if sys.version_info < (3, 7):
    print("錯誤: 需要 Python 3.7+")
    sys.exit(1)
```

## 進階參考

### 詳細技術文件

參考 [references/cross-platform-scripts.md](references/cross-platform-scripts.md) 以查看完整的技術參考，包括：

- 完整的程式碼範例和實作細節
- 各種常用模式的深入說明
- Windows 特定配置（VT Processing）
- 正則表達式模式
- HTTP 請求處理
- 更多進階範例

### 常見問題

**Q: 為什麼使用 subprocess 而非 os.system？**  
A: subprocess 提供更好的錯誤處理和輸出捕獲。

**Q: 可以使用 requests 庫嗎？**  
A: 優先使用 urllib.request（標準庫），除非需要複雜的 HTTP 功能。

**Q: Windows 7/8 支援彩色輸出嗎？**  
A: 會優雅降級為無色輸出，不會報錯。

## 經驗教訓

### 成功經驗

1. **Python 標準庫足夠強大**：無需外部依賴即可實現所有功能
2. **跨平台測試重要**：在 Windows/macOS/Linux 上都測試通過
3. **保持功能對等**：與 Bash 版本功能完全對等，降低遷移風險
4. **優雅降級**：Windows 舊版本無色輸出但不報錯

### 改進空間

1. **Python 版本檢查**：可新增 Python 3.7+ 版本檢查
2. **進度顯示**：可新增更友善的進度條
3. **配置檔案**：可支援外部配置檔案

---

**最後更新**: 2026-02-05  
**來源**: Task 8.8 - 本地開發 Docker 環境 Python 跨平台版本
