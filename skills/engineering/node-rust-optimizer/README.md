# Node.js Rust Optimizer

使用 NAPI-RS 優化 Node.js 後端效能的自動化工具。

## 適用場景

✅ 大型 JSON 解析與轉換 (> 10KB)  
✅ 複雜正規表示式批次過濾  
✅ 高頻率資料加密/解密  
✅ CPU 密集型資料處理  

## 效能提升

| 場景 | 加速比 |
|------|--------|
| JSON 解析 | 2-5x |
| Regex 過濾 | 3-10x |
| AES 加密 | 2-4x |

## 快速開始

### 1. 識別瓶頸

```bash
node scripts/identify_hotspots.js ./src
```

### 2. 建立 Rust 模組

```bash
npm install -g @napi-rs/cli
napi new my_optimizer
cd my_optimizer
```

### 3. 實作功能

參考 `assets/lib.rs.template` 中的範例。

### 4. 建置

```bash
npm run build
```

### 5. 整合

```javascript
const { parseJsonFast } = require('./my_optimizer');

const data = parseJsonFast(Buffer.from(jsonString));
```

## 目錄結構

```
node-rust-optimizer/
├── SKILL.md              # Skill 定義
├── README.md             # 本檔案
├── assets/               # 模板檔案
│   ├── Cargo.toml.template
│   ├── package.json.template
│   ├── lib.rs.template
│   └── index.d.ts.template
├── references/           # 參考文件
│   ├── napi_patterns.md
│   ├── project_structure.md
│   └── decision_matrix.md
└── scripts/              # 自動化腳本
    ├── identify_hotspots.js
    ├── rust_build_napi.sh
    └── static_analyzer.js
```

## 技術棧

- **NAPI-RS**: Rust ↔ Node.js 橋接
- **serde_json + simd-json**: 高效能 JSON 處理
- **regex**: Rust 正規表示式引擎
- **aes-gcm / ring**: 加密庫

## 最佳實踐

1. **只優化瓶頸**: 不要過早優化，先用工具識別真正的瓶頸
2. **Zero-Copy**: 使用 Buffer 避免記憶體拷貝
3. **非同步優先**: CPU 密集任務使用 `#[napi(ts_return_type = "Promise<T>")]`
4. **型別安全**: 維護 TypeScript 定義檔

## 參考資源

- [NAPI-RS 官方文件](https://napi.rs)
- [Rust Performance Book](https://nnethercote.github.io/perf-book/)
- [Node.js Profiling Guide](https://nodejs.org/en/docs/guides/simple-profiling/)
