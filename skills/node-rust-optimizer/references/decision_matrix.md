# 決策矩陣：何時使用 Rust 優化

## 快速決策表

| 場景 | 資料大小 | 頻率 | 建議 | 預期加速 |
|------|----------|------|------|----------|
| JSON 解析 | < 1KB | 任意 | ❌ 保留 JS | - |
| JSON 解析 | 1-10KB | < 100/s | ⚠️ 可選 | 1.5-2x |
| JSON 解析 | > 10KB | > 100/s | ✅ 使用 Rust | 2-5x |
| Regex 過濾 | 簡單模式 | < 1000/s | ❌ 保留 JS | - |
| Regex 過濾 | 複雜模式 | > 1000/s | ✅ 使用 Rust | 3-10x |
| 加密/解密 | < 1KB | < 100/s | ❌ 保留 JS | - |
| 加密/解密 | > 1KB | > 1000/s | ✅ 使用 Rust | 2-4x |
| 資料轉換 | 任意 | CPU > 30% | ✅ 使用 Rust | 2-5x |

## 詳細評估標準

### 1. JSON 處理

#### 使用 Rust 的條件

✅ **強烈建議**:
- JSON 大小 > 10KB
- 處理頻率 > 100 次/秒
- 包含大量陣列或巢狀結構
- 需要自訂解析邏輯

⚠️ **可選**:
- JSON 大小 1-10KB
- 處理頻率 10-100 次/秒
- 標準 JSON 結構

❌ **不建議**:
- JSON 大小 < 1KB
- 處理頻率 < 10 次/秒
- 簡單物件結構

#### 範例

```javascript
// ❌ 不值得優化
const small = JSON.parse('{"id":1,"name":"test"}');

// ✅ 值得優化
const large = JSON.parse(fs.readFileSync('10mb.json', 'utf8'));
```

### 2. 正規表示式

#### 使用 Rust 的條件

✅ **強烈建議**:
- 複雜模式 (> 50 字元)
- 批次匹配 (> 1000 項)
- 需要預編譯快取
- 回溯密集型模式

⚠️ **可選**:
- 中等複雜度模式
- 批次匹配 100-1000 項

❌ **不建議**:
- 簡單模式 (`^\d+$`, `^[a-z]+$`)
- 單次匹配
- 低頻率調用

#### 範例

```javascript
// ❌ 不值得優化
const simple = /^\d+$/.test(input);

// ✅ 值得優化
const emails = users.filter(u => 
  /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(u.email)
);
```

### 3. 加密/解密

#### 使用 Rust 的條件

✅ **強烈建議**:
- 資料大小 > 1MB
- 處理頻率 > 1000 次/秒
- 需要硬體加速 (AES-NI)
- 串流加密

⚠️ **可選**:
- 資料大小 100KB-1MB
- 處理頻率 100-1000 次/秒

❌ **不建議**:
- 資料大小 < 100KB
- 處理頻率 < 100 次/秒
- 使用 Node.js crypto 模組已足夠

#### 範例

```javascript
// ❌ 不值得優化
const encrypted = crypto.createCipher('aes-256-gcm', key)
  .update(smallData, 'utf8', 'hex');

// ✅ 值得優化
const stream = fs.createReadStream('large-file.bin')
  .pipe(rustEncryptStream(key));
```

### 4. 資料轉換

#### 使用 Rust 的條件

✅ **強烈建議**:
- CPU 使用率 > 30%
- 大量數學運算
- 記憶體密集型操作
- 需要 SIMD 優化

⚠️ **可選**:
- CPU 使用率 10-30%
- 中等複雜度運算

❌ **不建議**:
- CPU 使用率 < 10%
- 簡單資料映射
- I/O 密集型操作

## 成本效益分析

### 開發成本

| 項目 | 純 JS | JS + Rust |
|------|-------|-----------|
| 初始開發 | 1x | 2-3x |
| 維護成本 | 1x | 1.5x |
| 建置時間 | 快 | 慢 |
| 部署複雜度 | 低 | 中 |

### 效能收益

| 場景 | 開發成本 | 效能提升 | 值得嗎？ |
|------|----------|----------|----------|
| 小型 JSON | 2x | 1.2x | ❌ 否 |
| 大型 JSON | 2x | 3-5x | ✅ 是 |
| 簡單 Regex | 2x | 1.1x | ❌ 否 |
| 複雜 Regex | 2x | 5-10x | ✅ 是 |
| 小檔加密 | 2x | 1.5x | ❌ 否 |
| 大檔加密 | 2x | 3-4x | ✅ 是 |

## 實際案例

### 案例 1: API 閘道

**場景**: 每秒處理 10,000 個請求，每個請求需解析 5KB JSON

**分析**:
- 資料大小: 5KB (中等)
- 頻率: 10,000/s (極高)
- CPU 使用率: 45%

**決策**: ✅ 使用 Rust

**結果**:
- 延遲降低: 15ms → 5ms
- CPU 使用率: 45% → 20%
- 吞吐量提升: 2.5x

### 案例 2: 日誌過濾

**場景**: 每分鐘過濾 100,000 條日誌，使用複雜正規表示式

**分析**:
- 資料量: 100,000 項/分鐘
- Regex 複雜度: 高 (80+ 字元)
- CPU 使用率: 60%

**決策**: ✅ 使用 Rust

**結果**:
- 處理時間: 30s → 5s
- CPU 使用率: 60% → 15%
- 加速比: 6x

### 案例 3: 配置檔解析

**場景**: 啟動時解析 500KB JSON 配置檔

**分析**:
- 資料大小: 500KB (大)
- 頻率: 1 次/啟動 (極低)
- 影響: 啟動時間

**決策**: ❌ 不使用 Rust

**理由**: 頻率太低，開發成本不值得

## 決策流程圖

```
開始
  ↓
是否為效能瓶頸？
  ├─ 否 → 保留 JS
  └─ 是
      ↓
    資料大小或頻率是否足夠大？
      ├─ 否 → 保留 JS
      └─ 是
          ↓
        預期加速比 > 2x？
          ├─ 否 → 保留 JS
          └─ 是
              ↓
            開發成本可接受？
              ├─ 否 → 保留 JS
              └─ 是 → 使用 Rust
```

## 測量工具

### 識別瓶頸

```bash
# CPU Profiling
node --prof app.js
node --prof-process isolate-*.log

# 記憶體分析
node --inspect app.js
# 使用 Chrome DevTools

# 使用 clinic.js
clinic doctor -- node app.js
clinic flame -- node app.js
```

### 基準測試

```javascript
const Benchmark = require('benchmark');
const suite = new Benchmark.Suite;

suite
  .add('JS version', () => jsFunction(data))
  .add('Rust version', () => rustFunction(data))
  .on('cycle', event => console.log(String(event.target)))
  .on('complete', function() {
    console.log('Fastest is ' + this.filter('fastest').map('name'));
  })
  .run();
```

## 總結

**使用 Rust 的黃金法則**:
1. 先測量，後優化
2. 效能提升必須 > 2x
3. 考慮開發與維護成本
4. 優先優化熱點路徑
5. 保持介面簡單
