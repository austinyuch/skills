---
name: go-rust-optimizer
description: Go 效能瓶頸識別與 Rust 重構自動化工具。當需要優化 Go 專案效能、識別計算密集型熱點、將高負載迴圈轉換為 Rust、建立 CGO 橋接、支援 x86_64/ARM64 多架構部署、或在 Edge/Embedded 環境中達到極致效能時使用。適用於機器人控制、即時影像處理、路徑規劃、加密運算等高效能場景。
---

# Go-to-Rust Performance Engineer

## 概述

此 skill 提供系統化的 Go 效能優化流程，透過識別計算密集型熱點並使用 Rust 進行局部重構，達到極致的執行效率與記憶體安全性。特別適合 Edge Computing 與 Embedded Systems 環境。


## 核心原則

### Zero-Alloc 優先
Rust 端必須使用 `&[u8]` 而非 `Vec<u8>`，避免在嵌入式環境產生二次分配。

### CGO 防火牆
確保跨語言調用次數不超過迴圈外部，優先改寫「大循環」而非「小函式」，以抵銷 CGO 的上下文切換開銷。

### 硬體親和性
若運行於 ARM (Raspberry Pi/Jetson)，在 Rust 編譯器中開啟 `target-cpu=native` 優化。

### 安全護欄
在 Go 端必須使用 `defer` 或 `runtime.KeepAlive` 管理透過 CGO 傳遞的指針，防止執行中途發生 Segment Fault。

## 工作流程

### 階段 1: 識別與剖析 (Scanning & Profiling)

**目標**: 掃描代碼並找出高負載迴圈或高頻記憶體分配區塊。

**執行步驟**:

1. **動態分析**: 執行 `scripts/identify_hotspots.sh`
   - 自動執行 `go test -bench . -cpuprofile cpu.prof`
   - 使用 `go tool pprof` 解析輸出
   - 找出佔用 CPU 超過 15% 的函式

2. **靜態分析**: 執行 `scripts/static_analyzer.py <go-file-or-directory>`
   - 掃描迴圈內是否包含 `interface{}` 調用
   - 識別頻繁的 `append` 或大型結構體拷貝
   - 標記複雜數學運算

3. **決策評估**: 參考 `references/decision_matrix.md`
   - 評估資料大小 (< 1KB 保留 Go, > 100KB 使用 Rust)
   - 評估 CPU 使用率 (> 15% 強烈建議 Rust)
   - 評估 GC 壓力 (高壓力建議 Rust)

**識別規則**:
- **模式 A**: 複雜數學運算（矩陣、加密、信號處理）
- **模式 B**: 大量數據解析（自定義 Binary Protocol 轉換）
- **模式 C**: 高頻率的小物件分配導致 GC 壓力

### 階段 2: Rust 核心轉譯 (Rust Core Transpilation)

**目標**: 將識別出的 Go 函式轉譯為高效能 Rust 代碼。

**技術要求**:
- 使用 `extern "C"` 導出函數
- 強制使用 Zero-copy 策略：傳遞指針與長度，而非拷貝數據
- 利用 Rust 的 Iterators 與 SIMD 優化 Go 的 for 迴圈

**實作步驟**:

1. **建立 Rust 專案結構**:
   ```bash
   mkdir -p rust_core/src
   cp assets/Cargo.toml.template rust_core/Cargo.toml
   cp assets/cbindgen.toml.template rust_core/cbindgen.toml
   cp assets/lib.rs.template rust_core/src/lib.rs
   ```

2. **實作 Rust 函式**: 參考 `references/rust_ffi_patterns.md`
   - 使用 `#[no_mangle]` 和 `pub extern "C"`
   - 使用 `#[repr(C)]` 定義共享結構體
   - 加入 `// SAFETY:` 註解說明 unsafe 塊

3. **配置優化選項**:
   - `Cargo.toml`: 啟用 LTO、設定 `opt-level = 3`
   - ARM 環境: 加入 `target-feature=+neon`

### 階段 3: 整合與膠水代碼 (Integration & Glue)

**目標**: 使用 CGO 將 Rust 編譯的靜態庫連結回 Go。

**實作步驟**:

1. **編譯 Rust**: 執行 `scripts/rust_build_bridge.sh [rust_dir] [target_arch]`
   - 自動偵測或指定目標架構 (x86_64/arm64)
   - 編譯為靜態庫 `.a`
   - 生成 C header (使用 cbindgen)

2. **建立 Go 封裝**: 參考 `assets/sdk.go.template`
   - 建立 `sdk.go` 集中管理 CGO 定義
   - 加入 `// #cgo LDFLAGS` 標記
   - 實作型別轉換與安全檢查

3. **專案結構**: 參考 `references/project_structure.md`
   - 確保目錄結構符合標準
   - 配置 Makefile 自動化建置

### 階段 4: 驗證與基準測試 (Verification & Benchmarking)

**目標**: 確保邏輯正確並量化效能增益。

**測試步驟**:

1. **一致性測試**:
   ```go
   func TestConsistency(t *testing.T) {
       input := []float32{1, 2, 3, 4, 5}
       goResult := GoSumArray(input)
       rustResult := RustSumArray(input)
       if goResult != rustResult {
           t.Errorf("Mismatch: Go=%f, Rust=%f", goResult, rustResult)
       }
   }
   ```

2. **效能基準測試**:
   ```go
   func BenchmarkGoSum(b *testing.B) {
       data := make([]float32, 10000)
       for i := 0; i < b.N; i++ {
           GoSumArray(data)
       }
   }
   
   func BenchmarkRustSum(b *testing.B) {
       data := make([]float32, 10000)
       for i := 0; i < b.N; i++ {
           RustSumArray(data)
       }
   }
   ```

3. **退回機制**:
   - 若 Rust 版效能提升低於 10%，標註原因並考慮回退
   - 若出現記憶體洩漏，立即回退並修復

**預期結果**:
- 效能提升至少 1.5x (開發環境)
- 效能提升至少 2x (生產環境)
- 效能提升至少 3x (嵌入式環境)

## 多架構部署

### 支援架構
- x86_64 (amd64)
- aarch64 (arm64)

### Docker Multi-stage Build

參考 `references/project_structure.md` 中的 Dockerfile 範例：
- 使用 `--platform=$BUILDPLATFORM` 支援多架構
- 使用 Multi-stage build 減少最終鏡像大小
- 靜態連結避免 glibc 版本不相容

### 建置命令

```bash
# 本地開發
make all

# 交叉編譯 ARM64
make all TARGET_ARCH=arm64

# Docker 多架構
docker buildx build --platform linux/amd64,linux/arm64 -t myapp:latest .
```

## 環境自檢

完成建置後，執行以下檢查：

1. **符號表檢查**:
   ```bash
   nm ./lib/librust_core.a | grep rust_
   ```
   確認函數符號已正確導出。

2. **動態連結檢查**:
   ```bash
   ldd edge_app
   ```
   確認沒有遺失動態連結庫。

3. **執行測試**:
   ```bash
   make test
   ```
   確認所有測試通過且效能符合預期。

## 完成定義 (Definition of Done)

- ✅ 自動 Profiling: 已執行 `go test -bench` 並回報效能瓶頸
- ✅ 型別安全: 已透過 cbindgen 生成標頭檔
- ✅ 邊界檢查: sdk.go 中已檢查 `len(input) == 0`
- ✅ 連結驗證: Makefile 執行完後，edge_app 可在目標硬體上執行
- ✅ 效能驗證: Rust 版本效能提升達到預期閾值
- ✅ 記憶體安全: 所有 unsafe 塊已加入 SAFETY 註解
- ✅ 多架構支援: 已測試 x86_64 和 arm64 建置

## 參考資料

詳細技術細節請參考：
- `references/rust_ffi_patterns.md` - Rust FFI 模式與最佳實踐
- `references/project_structure.md` - 專案結構與建置配置
- `references/decision_matrix.md` - 決策矩陣：何時使用 Rust 優化

## 範例使用

```bash
# 1. 識別熱點
./scripts/identify_hotspots.sh
./scripts/static_analyzer.py ./myproject

# 2. 建立 Rust 專案
mkdir -p rust_core/src
cp assets/*.template rust_core/

# 3. 實作 Rust 函式 (參考 references/rust_ffi_patterns.md)

# 4. 建置與測試
./scripts/rust_build_bridge.sh rust_core x86_64
make test

# 5. 部署
docker buildx build --platform linux/amd64,linux/arm64 -t myapp:latest .
```
