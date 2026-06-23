---
name: node-rust-optimizer
description: Node.js 後端效能瓶頸識別與 Rust 優化工具。專注於大型 JSON 解析轉換、複雜正規表示式過濾、高效能資料加密。使用 NAPI-RS 建立零成本抽象的原生模組，適用於高流量 API、資料處理管道、即時系統等場景。
---

# Node.js-to-Rust Performance Optimizer

## 概述

此 skill 提供系統化的 Node.js 後端效能優化流程，透過 NAPI-RS 將計算密集型操作轉移至 Rust，達到極致效能與記憶體安全。

## 核心場景

### 1. 大型 JSON 解析與轉換
- 使用 `serde_json` + `simd-json` 加速解析
- 零拷貝 Buffer 傳遞
- 批次處理優化

### 2. 複雜正規表示式過濾
- 使用 Rust `regex` crate 的高效能引擎
- 預編譯模式快取
- 批次匹配優化

### 3. 高效能資料加密
- 使用 `ring` / `aes-gcm` 等加密庫
- 硬體加速支援 (AES-NI)
- 串流加密處理

## 核心原則

### Zero-Copy 優先
使用 Node.js Buffer 和 TypedArray，避免 JavaScript ↔ Rust 的資料拷貝。

### 非同步優先
利用 `tokio` runtime 處理 CPU 密集任務，避免阻塞事件迴圈。

### 型別安全
使用 TypeScript 定義檔 (.d.ts) 確保型別正確性。

### 效能門檻
Rust 版本必須比純 JS 版本快至少 2x，否則不值得引入複雜度。

## 工作流程

### 階段 1: 識別與剖析 (Profiling)

**目標**: 找出 Node.js 應用中的效能瓶頸。

**執行步驟**:

1. **動態分析**: 執行 `node --prof app.js` 或使用 `clinic.js`
   ```bash
   npm install -g clinic
   clinic doctor -- node app.js
   ```

2. **靜態分析**: 執行 `scripts/static_analyzer.js`
   ```bash
   node scripts/static_analyzer.js ./src
   ```
   自動識別：
   - 大型 JSON.parse/stringify 調用
   - 複雜正規表示式 (超過 50 字元)
   - 加密/解密操作

3. **決策評估**: 參考 `references/decision_matrix.md`
   - JSON 大小 > 10KB → 考慮 Rust
   - Regex 複雜度高 + 高頻調用 → 使用 Rust
   - 加密操作 > 1000 次/秒 → 使用 Rust

### 階段 2: Rust 模組開發 (NAPI-RS)

**目標**: 使用 NAPI-RS 建立高效能原生模組。

**實作步驟**:

1. **初始化專案**:
   ```bash
   npm install -g @napi-rs/cli
   napi new rust_core
   cd rust_core
   ```

2. **配置依賴**: 編輯 `Cargo.toml`
   ```toml
   [dependencies]
   napi = "2"
   napi-derive = "2"
   serde_json = "1"
   simd-json = "0.13"
   regex = "1"
   aes-gcm = "0.10"
   ```

3. **實作函式**: 參考 `references/napi_patterns.md`
   
   **JSON 解析範例**:
   ```rust
   #[napi]
   pub fn parse_json_fast(input: Buffer) -> Result<JsUnknown> {
       let mut bytes = input.as_ref().to_vec();
       let value = simd_json::to_borrowed_value(&mut bytes)?;
       // 轉換為 JS 物件
   }
   ```

   **Regex 過濾範例**:
   ```rust
   #[napi]
   pub fn filter_regex(pattern: String, texts: Vec<String>) -> Vec<String> {
       let re = Regex::new(&pattern).unwrap();
       texts.into_iter().filter(|t| re.is_match(t)).collect()
   }
   ```

   **加密範例**:
   ```rust
   #[napi]
   pub fn encrypt_aes(key: Buffer, data: Buffer) -> Result<Buffer> {
       // AES-GCM 加密實作
   }
   ```

### 階段 3: 建置與整合 (Build & Integration)

**目標**: 編譯 Rust 模組並整合到 Node.js 專案。

**實作步驟**:

1. **建置**: 執行 `scripts/rust_build_napi.sh`
   ```bash
   ./scripts/rust_build_napi.sh
   ```
   自動處理：
   - 多平台編譯 (Linux/macOS/Windows)
   - 產生 .node 檔案
   - 產生 TypeScript 定義

2. **整合到專案**:
   ```javascript
   const { parseJsonFast, filterRegex, encryptAes } = require('./rust_core');
   
   // 使用
   const data = parseJsonFast(buffer);
   const filtered = filterRegex('^user_', usernames);
   const encrypted = encryptAes(key, plaintext);
   ```

3. **TypeScript 支援**:
   ```typescript
   import { parseJsonFast, filterRegex, encryptAes } from './rust_core';
   
   const data: unknown = parseJsonFast(buffer);
   const filtered: string[] = filterRegex('^user_', usernames);
   ```

### 階段 4: 驗證與基準測試 (Benchmarking)

**目標**: 確保邏輯正確並量化效能增益。

**測試步驟**:

1. **功能測試**:
   ```javascript
   const assert = require('assert');
   
   // JSON 解析一致性
   const jsResult = JSON.parse(jsonString);
   const rustResult = parseJsonFast(Buffer.from(jsonString));
   assert.deepEqual(jsResult, rustResult);
   ```

2. **效能基準測試**:
   ```javascript
   const Benchmark = require('benchmark');
   const suite = new Benchmark.Suite;
   
   suite
     .add('JSON.parse', () => JSON.parse(largeJson))
     .add('Rust parse', () => parseJsonFast(largeJsonBuffer))
     .on('cycle', event => console.log(String(event.target)))
     .run();
   ```

**預期結果**:
- JSON 解析: 2-5x 加速
- Regex 過濾: 3-10x 加速
- 加密操作: 2-4x 加速

## 多平台支援

### 支援平台
- Linux (x64, arm64)
- macOS (x64, arm64)
- Windows (x64)

### 預編譯二進位
使用 GitHub Actions 自動建置：
```yaml
- uses: actions/setup-node@v3
- run: npm install
- run: npm run build
- run: npm run build:release
```

## 完成定義 (Definition of Done)

- ✅ 效能分析: 已識別瓶頸並確認適合 Rust 優化
- ✅ 型別安全: 已產生 TypeScript 定義檔
- ✅ 功能驗證: 所有測試通過，結果與 JS 版本一致
- ✅ 效能驗證: Rust 版本至少快 2x
- ✅ 多平台: 已測試 Linux/macOS/Windows
- ✅ 文件完整: README 包含使用範例和效能數據

## 參考資料

- `references/napi_patterns.md` - NAPI-RS 模式與最佳實踐
- `references/project_structure.md` - 專案結構與建置配置
- `references/decision_matrix.md` - 決策矩陣：何時使用 Rust

## 快速開始

```bash
# 1. 分析效能瓶頸
node scripts/identify_hotspots.js ./src

# 2. 建立 Rust 模組
napi new rust_core
cd rust_core

# 3. 實作功能 (參考 assets/*.template)

# 4. 建置
./scripts/rust_build_napi.sh

# 5. 測試
npm test
npm run bench

# 6. 整合到專案
npm install ./rust_core
```
