# NAPI-RS 模式與最佳實踐

## 基本模式

### 1. 同步函式

```rust
#[napi]
pub fn sync_function(input: String) -> Result<String> {
    Ok(input.to_uppercase())
}
```

### 2. 非同步函式

```rust
#[napi(ts_return_type = "Promise<string>")]
pub async fn async_function(input: String) -> Result<String> {
    tokio::time::sleep(Duration::from_secs(1)).await;
    Ok(input.to_uppercase())
}
```

### 3. Buffer 處理 (Zero-Copy)

```rust
#[napi]
pub fn process_buffer(input: Buffer) -> Result<Buffer> {
    let data = input.as_ref(); // 零拷貝讀取
    let processed = data.iter().map(|b| b.wrapping_add(1)).collect();
    Ok(Buffer::from(processed))
}
```

## 型別對應

| Rust | Node.js | TypeScript |
|------|---------|------------|
| `String` | `string` | `string` |
| `i32, u32` | `number` | `number` |
| `bool` | `boolean` | `boolean` |
| `Vec<T>` | `Array` | `T[]` |
| `Buffer` | `Buffer` | `Buffer` |
| `Option<T>` | `T \| null` | `T \| null` |
| `Result<T>` | throws | `T` |

## 效能最佳化

### 1. 避免不必要的拷貝

❌ **錯誤**:
```rust
#[napi]
pub fn bad(input: String) -> String {
    input.clone() // 不必要的拷貝
}
```

✅ **正確**:
```rust
#[napi]
pub fn good(input: String) -> String {
    input // 直接移動所有權
}
```

### 2. 使用 Buffer 而非 String

❌ **錯誤** (二進位資料):
```rust
#[napi]
pub fn bad(data: String) -> String {
    // String 會進行 UTF-8 驗證，效能損失
}
```

✅ **正確**:
```rust
#[napi]
pub fn good(data: Buffer) -> Buffer {
    // Buffer 是原始位元組，無驗證開銷
}
```

### 3. 批次處理

❌ **錯誤**:
```javascript
for (const item of items) {
    rustFunction(item); // 多次跨語言調用
}
```

✅ **正確**:
```rust
#[napi]
pub fn batch_process(items: Vec<String>) -> Vec<String> {
    items.into_iter().map(|s| s.to_uppercase()).collect()
}
```

## 錯誤處理

### 1. 使用 Result

```rust
#[napi]
pub fn may_fail(input: String) -> Result<String> {
    if input.is_empty() {
        return Err(Error::from_reason("Input cannot be empty"));
    }
    Ok(input.to_uppercase())
}
```

### 2. 自訂錯誤訊息

```rust
use napi::Error;

#[napi]
pub fn validate(age: i32) -> Result<String> {
    if age < 0 {
        return Err(Error::from_reason(format!("Invalid age: {}", age)));
    }
    Ok(format!("Age is {}", age))
}
```

## 非同步模式

### 1. CPU 密集任務

```rust
#[napi(ts_return_type = "Promise<number>")]
pub async fn cpu_intensive(n: u64) -> Result<u64> {
    tokio::task::spawn_blocking(move || {
        // 在獨立執行緒執行，不阻塞事件迴圈
        (0..n).sum()
    }).await.map_err(|e| Error::from_reason(e.to_string()))
}
```

### 2. I/O 操作

```rust
#[napi(ts_return_type = "Promise<string>")]
pub async fn read_file(path: String) -> Result<String> {
    tokio::fs::read_to_string(path)
        .await
        .map_err(|e| Error::from_reason(e.to_string()))
}
```

## 記憶體管理

### 1. 避免記憶體洩漏

```rust
#[napi]
pub fn safe_function(input: Buffer) -> Result<Buffer> {
    let data = input.as_ref(); // 借用，不取得所有權
    let result = process(data);
    Ok(Buffer::from(result)) // 新 Buffer 由 Node.js GC 管理
}
```

### 2. 大型資料處理

```rust
#[napi]
pub fn stream_process(input: Buffer) -> Result<Buffer> {
    // 使用迭代器避免一次性載入全部資料
    let result: Vec<u8> = input.as_ref()
        .iter()
        .map(|&b| b.wrapping_mul(2))
        .collect();
    Ok(Buffer::from(result))
}
```

## 測試

### Rust 單元測試

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_function() {
        let result = sync_function("hello".to_string()).unwrap();
        assert_eq!(result, "HELLO");
    }
}
```

### Node.js 整合測試

```javascript
const assert = require('assert');
const { syncFunction } = require('./index');

assert.strictEqual(syncFunction('hello'), 'HELLO');
```
