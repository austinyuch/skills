# Rust FFI 模式與最佳實踐

## Zero-Copy 資料傳遞

### Go Slice → Rust Slice

**Go 端 (sdk.go)**:
```go
func CallRust(data []float32) float32 {
    if len(data) == 0 {
        return 0
    }
    ptr := (*C.float)(unsafe.Pointer(&data[0]))
    length := C.uintptr_t(len(data))
    
    // 防止 GC 在 Rust 執行期間回收
    defer runtime.KeepAlive(data)
    
    return float32(C.rust_function(ptr, length))
}
```

**Rust 端 (lib.rs)**:
```rust
#[no_mangle]
pub extern "C" fn rust_function(ptr: *const f32, len: usize) -> f32 {
    let data = unsafe {
        assert!(!ptr.is_null());
        std::slice::from_raw_parts(ptr, len)
    };
    
    // Zero-copy: 直接操作 Go 的記憶體
    data.iter().sum()
}
```

## 結構體傳遞

### 使用 #[repr(C)] 確保記憶體對齊

**Rust 端**:
```rust
#[repr(C)]
pub struct SensorData {
    pub id: i32,
    pub value: f32,
}

#[no_mangle]
pub extern "C" fn process_sensors(ptr: *const SensorData, len: usize) -> f32 {
    let data = unsafe { std::slice::from_raw_parts(ptr, len) };
    data.iter().map(|s| s.value).sum()
}
```

**Go 端 (使用 cbindgen 生成的 header)**:
```go
/*
#include "./include/rust_core.h"
*/
import "C"

func ProcessSensors(data []C.SensorData) float32 {
    if len(data) == 0 { return 0 }
    ptr := (*C.SensorData)(unsafe.Pointer(&data[0]))
    defer runtime.KeepAlive(data)
    return float32(C.process_sensors(ptr, C.uintptr_t(len(data))))
}
```

## SIMD 優化

### 使用 Rust Iterator 與 SIMD

```rust
use std::simd::*;

#[no_mangle]
pub extern "C" fn simd_sum(ptr: *const f32, len: usize) -> f32 {
    let data = unsafe { std::slice::from_raw_parts(ptr, len) };
    
    // 使用 SIMD 加速
    data.chunks_exact(4)
        .map(|chunk| {
            let v = f32x4::from_slice(chunk);
            v.reduce_sum()
        })
        .sum::<f32>()
        + data.chunks_exact(4).remainder().iter().sum::<f32>()
}
```

## 錯誤處理

### 使用 Result 與錯誤碼

**Rust 端**:
```rust
#[repr(C)]
pub struct RustResult {
    pub value: f32,
    pub error_code: i32,  // 0 = success, -1 = error
}

#[no_mangle]
pub extern "C" fn safe_divide(a: f32, b: f32) -> RustResult {
    if b == 0.0 {
        return RustResult { value: 0.0, error_code: -1 };
    }
    RustResult { value: a / b, error_code: 0 }
}
```

**Go 端**:
```go
func SafeDivide(a, b float32) (float32, error) {
    result := C.safe_divide(C.float(a), C.float(b))
    if result.error_code != 0 {
        return 0, fmt.Errorf("division error")
    }
    return float32(result.value), nil
}
```

## 記憶體安全檢查清單

- ✅ 使用 `assert!(!ptr.is_null())` 檢查空指針
- ✅ Go 端使用 `runtime.KeepAlive()` 防止 GC
- ✅ Rust 端使用 `#[repr(C)]` 確保 ABI 相容
- ✅ 所有 `unsafe` 塊加入 `// SAFETY:` 註解
- ✅ 邊界檢查：`len(data) == 0` 處理
- ✅ 使用 `defer` 確保資源清理
