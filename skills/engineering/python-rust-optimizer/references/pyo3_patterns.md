# PyO3 模式與最佳實踐

## 基本 PyO3 函式

### 簡單函式導出

**Rust 端 (lib.rs)**:
```rust
use pyo3::prelude::*;

#[pyfunction]
fn sum_array(data: Vec<f32>) -> f32 {
    data.iter().sum()
}

#[pymodule]
fn rust_ext(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_array, m)?)?;
    Ok(())
}
```

**Python 端**:
```python
import rust_ext

result = rust_ext.sum_array([1.0, 2.0, 3.0, 4.0])
print(result)  # 10.0
```

## Zero-Copy with NumPy

### 使用 numpy crate

**Cargo.toml**:
```toml
[dependencies]
pyo3 = { version = "0.20", features = ["extension-module"] }
numpy = "0.20"
```

**Rust 端**:
```rust
use numpy::{PyArray1, PyReadonlyArray1};
use pyo3::prelude::*;

#[pyfunction]
fn process_numpy<'py>(
    py: Python<'py>,
    arr: PyReadonlyArray1<f64>
) -> &'py PyArray1<f64> {
    let arr = arr.as_array();
    
    // Zero-copy: 直接操作 NumPy 記憶體
    let result: Vec<f64> = arr.iter()
        .map(|&x| x * 2.0)
        .collect();
    
    PyArray1::from_vec(py, result)
}
```

**Python 端**:
```python
import numpy as np
import rust_ext

data = np.array([1.0, 2.0, 3.0], dtype=np.float64)
result = rust_ext.process_numpy(data)
print(result)  # [2. 4. 6.]
```

## 類別與方法

### 導出 Python 類別

**Rust 端**:
```rust
use pyo3::prelude::*;

#[pyclass]
struct Point {
    #[pyo3(get, set)]
    x: f64,
    #[pyo3(get, set)]
    y: f64,
}

#[pymethods]
impl Point {
    #[new]
    fn new(x: f64, y: f64) -> Self {
        Point { x, y }
    }
    
    fn distance(&self, other: &Point) -> f64 {
        let dx = self.x - other.x;
        let dy = self.y - other.y;
        (dx * dx + dy * dy).sqrt()
    }
    
    fn __repr__(&self) -> String {
        format!("Point({}, {})", self.x, self.y)
    }
}

#[pymodule]
fn rust_ext(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<Point>()?;
    Ok(())
}
```

**Python 端**:
```python
from rust_ext import Point

p1 = Point(0.0, 0.0)
p2 = Point(3.0, 4.0)
print(p1.distance(p2))  # 5.0
print(p1)  # Point(0, 0)
```

## 錯誤處理

### PyResult 與異常

**Rust 端**:
```rust
use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;

#[pyfunction]
fn safe_divide(a: f64, b: f64) -> PyResult<f64> {
    if b == 0.0 {
        Err(PyValueError::new_err("Division by zero"))
    } else {
        Ok(a / b)
    }
}
```

**Python 端**:
```python
import rust_ext

try:
    result = rust_ext.safe_divide(10.0, 0.0)
except ValueError as e:
    print(f"Error: {e}")  # Error: Division by zero
```

## 並行處理

### 使用 Rayon 並行化

**Cargo.toml**:
```toml
[dependencies]
pyo3 = { version = "0.20", features = ["extension-module"] }
rayon = "1.8"
```

**Rust 端**:
```rust
use pyo3::prelude::*;
use rayon::prelude::*;

#[pyfunction]
fn parallel_sum(data: Vec<f64>) -> f64 {
    // 釋放 GIL 以允許並行
    data.par_iter().sum()
}

#[pyfunction]
fn parallel_process(py: Python, data: Vec<f64>) -> Vec<f64> {
    // 釋放 GIL
    py.allow_threads(|| {
        data.par_iter()
            .map(|&x| x.powi(2))
            .collect()
    })
}
```

## GIL 管理

### 釋放 GIL 提升並行效能

**Rust 端**:
```rust
use pyo3::prelude::*;

#[pyfunction]
fn cpu_intensive(py: Python, n: usize) -> u64 {
    // 釋放 GIL，允許其他 Python 執行緒執行
    py.allow_threads(|| {
        (0..n).map(|i| i as u64).sum()
    })
}
```

## 效能最佳實踐

### 1. 避免不必要的轉換

```rust
// ❌ 不好：每次都轉換
#[pyfunction]
fn bad_sum(data: Vec<f64>) -> f64 {
    data.iter().sum()  // Vec 已經分配記憶體
}

// ✅ 好：使用 slice
#[pyfunction]
fn good_sum(data: &[f64]) -> f64 {
    data.iter().sum()  // 借用，無額外分配
}
```

### 2. 使用 NumPy 進行大陣列

```rust
// ✅ 對大陣列使用 NumPy
use numpy::PyReadonlyArray1;

#[pyfunction]
fn process_large(arr: PyReadonlyArray1<f64>) -> f64 {
    arr.as_array().iter().sum()
}
```

### 3. 批次處理

```rust
// ✅ 批次處理減少 Python/Rust 邊界跨越
#[pyfunction]
fn batch_process(data: Vec<Vec<f64>>) -> Vec<f64> {
    data.into_iter()
        .map(|batch| batch.iter().sum())
        .collect()
}
```

## 記憶體安全檢查清單

- ✅ 使用 `PyReadonlyArray` 進行只讀 NumPy 陣列
- ✅ 使用 `py.allow_threads()` 釋放 GIL
- ✅ 避免在 Rust 端持有 Python 物件太久
- ✅ 使用 `PyResult` 處理錯誤
- ✅ 大型計算使用 Rayon 並行化
- ✅ 使用 `&[T]` 而非 `Vec<T>` 減少複製
