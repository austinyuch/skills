# Go-to-Rust Optimizer Skill

## 概述

已成功建立 `go-rust-optimizer` skill，這是一個完整的 Go 效能瓶頸識別與 Rust 重構自動化工具。

## Skill 內容

### 核心功能

1. **識別與剖析** - 自動掃描 Go 代碼找出效能瓶頸
2. **Rust 核心轉譯** - 將熱點轉換為高效能 Rust 代碼
3. **整合與膠水代碼** - 使用 CGO 橋接 Go 與 Rust
4. **驗證與基準測試** - 確保邏輯正確並量化效能增益

### 檔案結構

```
go-rust-optimizer/
├── SKILL.md                          # 主要 skill 文件
├── scripts/                          # 自動化腳本
│   ├── identify_hotspots.sh         # 動態效能分析
│   ├── rust_build_bridge.sh         # Rust 建置與橋接
│   └── static_analyzer.py           # 靜態代碼分析
├── references/                       # 參考文件
│   ├── rust_ffi_patterns.md         # Rust FFI 模式
│   ├── project_structure.md         # 專案結構與建置
│   └── decision_matrix.md           # 決策矩陣
└── assets/                           # 範本檔案
    ├── Cargo.toml.template          # Rust 專案配置
    ├── cbindgen.toml.template       # C header 生成配置
    ├── lib.rs.template              # Rust 函式庫範本
    └── sdk.go.template              # Go CGO 橋接範本
```

## 主要特色

### 1. 完整的四階段工作流程

- **階段 1**: 識別與剖析 (動態 + 靜態分析)
- **階段 2**: Rust 核心轉譯 (Zero-copy + SIMD)
- **階段 3**: 整合與膠水代碼 (CGO 橋接)
- **階段 4**: 驗證與基準測試 (一致性 + 效能)

### 2. 多架構支援

- x86_64 (amd64)
- aarch64 (arm64)
- Docker Multi-stage Build
- 交叉編譯支援

### 3. 安全性保證

- Zero-Alloc 優先原則
- CGO 防火牆策略
- 記憶體安全檢查
- runtime.KeepAlive 防護

### 4. 決策支援

- 資料大小閾值評估
- CPU 使用率分析
- GC 壓力評估
- 效能增益預期

## 使用場景

適用於：
- 機器人控制系統
- 即時影像處理
- 路徑規劃演算法
- 加密運算
- Edge Computing
- Embedded Systems

## 效能目標

- 開發環境: 至少 1.5x 加速
- 生產環境: 至少 2x 加速
- 嵌入式環境: 至少 3x 加速

## 快速開始

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

## 技術亮點

### Rust FFI 模式
- Zero-copy 資料傳遞
- #[repr(C)] 記憶體對齊
- SIMD 優化
- 結構化錯誤處理

### 專案結構標準化
- 標準目錄佈局
- Makefile 自動化
- cbindgen 整合
- Docker 多階段建置

### 決策矩陣
- 資料大小評估
- 運算類型分類
- GC 壓力分析
- 實際案例參考

## 完成定義 (DoD)

- ✅ 自動 Profiling
- ✅ 型別安全 (cbindgen)
- ✅ 邊界檢查
- ✅ 連結驗證
- ✅ 效能驗證
- ✅ 記憶體安全
- ✅ 多架構支援

## 輸出檔案

已打包為: `/home/ac/.kiro/skills/go-rust-optimizer.skill`

可以直接分享給使用者安裝使用。
