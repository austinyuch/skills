# 專案結構與建置配置

## 標準專案結構

```
my-node-app/
├── rust_core/              # Rust 原生模組
│   ├── src/
│   │   └── lib.rs         # Rust 實作
│   ├── Cargo.toml         # Rust 依賴
│   ├── package.json       # NPM 配置
│   ├── build.rs           # 建置腳本
│   └── index.d.ts         # TypeScript 定義
├── src/                   # Node.js 應用程式
│   ├── index.js
│   └── utils.js
├── test/                  # 測試
│   ├── unit.test.js
│   └── bench.js
└── package.json           # 主專案配置
```

## Cargo.toml 配置

```toml
[package]
name = "rust_core"
version = "0.1.0"
edition = "2021"

[lib]
crate-type = ["cdylib"]  # 動態連結庫

[dependencies]
napi = "2"
napi-derive = "2"
# 根據需求添加其他依賴

[build-dependencies]
napi-build = "2"

[profile.release]
lto = true              # Link-Time Optimization
codegen-units = 1       # 單一編譯單元，更好的優化
opt-level = 3           # 最高優化等級
strip = true            # 移除除錯符號
```

## package.json 配置

```json
{
  "name": "rust_core",
  "version": "0.1.0",
  "main": "index.js",
  "types": "index.d.ts",
  "napi": {
    "name": "rust_core",
    "triples": {
      "defaults": true,
      "additional": [
        "aarch64-apple-darwin",
        "aarch64-unknown-linux-gnu"
      ]
    }
  },
  "scripts": {
    "build": "napi build --platform --release",
    "build:debug": "napi build --platform",
    "prepublishOnly": "napi prepublish -t npm",
    "artifacts": "napi artifacts",
    "version": "napi version"
  }
}
```

## 建置流程

### 本地開發

```bash
# 除錯建置 (快速，包含除錯符號)
npm run build:debug

# 發布建置 (優化，體積小)
npm run build
```

### CI/CD (GitHub Actions)

```yaml
name: Build

on: [push, pull_request]

jobs:
  build:
    strategy:
      matrix:
        settings:
          - host: ubuntu-latest
            target: x86_64-unknown-linux-gnu
          - host: macos-latest
            target: x86_64-apple-darwin
          - host: macos-latest
            target: aarch64-apple-darwin
          - host: windows-latest
            target: x86_64-pc-windows-msvc

    runs-on: ${{ matrix.settings.host }}

    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      
      - name: Install Rust
        uses: dtolnay/rust-toolchain@stable
        with:
          targets: ${{ matrix.settings.target }}
      
      - name: Build
        run: |
          npm install
          npm run build
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: bindings-${{ matrix.settings.target }}
          path: rust_core/*.node
```

## 多平台支援

### 支援的平台

| 平台 | 架構 | Target Triple |
|------|------|---------------|
| Linux | x64 | x86_64-unknown-linux-gnu |
| Linux | ARM64 | aarch64-unknown-linux-gnu |
| macOS | x64 | x86_64-apple-darwin |
| macOS | ARM64 | aarch64-apple-darwin |
| Windows | x64 | x86_64-pc-windows-msvc |

### 交叉編譯

```bash
# 安裝目標平台工具鏈
rustup target add aarch64-unknown-linux-gnu

# 建置
npm run build -- --target aarch64-unknown-linux-gnu
```

## 發布到 NPM

### 1. 預編譯二進位

```bash
# 建置所有平台
npm run build

# 打包 artifacts
npm run artifacts

# 發布
npm publish
```

### 2. 可選依賴 (Optional Dependencies)

```json
{
  "optionalDependencies": {
    "@my-package/linux-x64": "0.1.0",
    "@my-package/darwin-x64": "0.1.0",
    "@my-package/darwin-arm64": "0.1.0",
    "@my-package/win32-x64": "0.1.0"
  }
}
```

## 整合到主專案

### 方式 1: 本地路徑

```json
{
  "dependencies": {
    "rust_core": "file:./rust_core"
  }
}
```

### 方式 2: NPM 套件

```json
{
  "dependencies": {
    "rust_core": "^0.1.0"
  }
}
```

### 使用

```javascript
// CommonJS
const { parseJsonFast } = require('rust_core');

// ES Module
import { parseJsonFast } from 'rust_core';

// TypeScript
import { parseJsonFast } from 'rust_core';
const result: string = parseJsonFast(buffer);
```

## 除錯

### Rust 端

```bash
# 啟用除錯日誌
RUST_LOG=debug node app.js

# 使用 lldb/gdb
lldb -- node app.js
```

### Node.js 端

```bash
# 使用 Node.js inspector
node --inspect-brk app.js
```

## 效能分析

### Rust 端

```bash
# 使用 perf (Linux)
perf record -g node app.js
perf report

# 使用 Instruments (macOS)
instruments -t "Time Profiler" node app.js
```

### Node.js 端

```bash
# 使用 clinic.js
clinic doctor -- node app.js
clinic flame -- node app.js
```
