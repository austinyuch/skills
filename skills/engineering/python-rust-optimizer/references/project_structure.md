# 專案結構與建置配置

## 標準目錄結構

```
project/
├── pyproject.toml          # Python 專案配置
├── Cargo.toml              # Rust 專案配置
├── src/
│   └── lib.rs              # Rust 擴展實作
├── python/
│   └── myproject/
│       ├── __init__.py
│       └── wrapper.py      # Python 封裝層
├── tests/
│   ├── test_rust_ext.py
│   └── benchmark.py
└── README.md
```

## Cargo.toml 配置

```toml
[package]
name = "rust_ext"
version = "0.1.0"
edition = "2021"

[lib]
name = "rust_ext"
crate-type = ["cdylib"]

[dependencies]
pyo3 = { version = "0.20", features = ["extension-module"] }
numpy = "0.20"
rayon = "1.8"

[profile.release]
opt-level = 3
lto = true
codegen-units = 1
strip = true

# ARM 特定優化
[target.aarch64-unknown-linux-gnu]
rustflags = ["-C", "target-feature=+neon"]
```

## pyproject.toml 配置

```toml
[build-system]
requires = ["maturin>=1.0,<2.0"]
build-backend = "maturin"

[project]
name = "myproject"
version = "0.1.0"
requires-python = ">=3.8"
dependencies = [
    "numpy>=1.20",
]

[tool.maturin]
python-source = "python"
module-name = "myproject.rust_ext"
```

## 建置與開發

### 使用 Maturin

```bash
# 安裝 maturin
pip install maturin

# 開發模式（快速迭代）
maturin develop

# 發布模式
maturin build --release

# 安裝 wheel
pip install target/wheels/*.whl
```

### 使用 setuptools-rust (替代方案)

**setup.py**:
```python
from setuptools import setup
from setuptools_rust import Binding, RustExtension

setup(
    name="myproject",
    version="0.1.0",
    rust_extensions=[
        RustExtension(
            "myproject.rust_ext",
            binding=Binding.PyO3,
            debug=False,
        )
    ],
    packages=["myproject"],
    zip_safe=False,
)
```

## 測試配置

### pytest 整合

**tests/test_rust_ext.py**:
```python
import pytest
import numpy as np
from myproject import rust_ext

def test_sum_array():
    data = [1.0, 2.0, 3.0, 4.0]
    result = rust_ext.sum_array(data)
    assert result == 10.0

def test_numpy_processing():
    data = np.array([1.0, 2.0, 3.0], dtype=np.float64)
    result = rust_ext.process_numpy(data)
    expected = np.array([2.0, 4.0, 6.0])
    np.testing.assert_array_almost_equal(result, expected)

@pytest.mark.benchmark
def test_benchmark(benchmark):
    data = np.random.rand(10000)
    result = benchmark(rust_ext.process_numpy, data)
```

### Benchmark 比較

**tests/benchmark.py**:
```python
import time
import numpy as np
from myproject import rust_ext

def python_sum(data):
    return sum(data)

def benchmark_comparison():
    data = np.random.rand(1000000).tolist()
    
    # Python 版本
    start = time.time()
    py_result = python_sum(data)
    py_time = time.time() - start
    
    # Rust 版本
    start = time.time()
    rust_result = rust_ext.sum_array(data)
    rust_time = time.time() - start
    
    print(f"Python: {py_time:.4f}s")
    print(f"Rust:   {rust_time:.4f}s")
    print(f"Speedup: {py_time/rust_time:.2f}x")
    
    assert abs(py_result - rust_result) < 1e-6

if __name__ == "__main__":
    benchmark_comparison()
```

## Docker Multi-stage Build

```dockerfile
FROM rust:1.75 AS rust-builder

WORKDIR /app
COPY Cargo.toml Cargo.lock ./
COPY src ./src

RUN cargo build --release

FROM python:3.11-slim

RUN pip install maturin

WORKDIR /app
COPY --from=rust-builder /app/target/release/*.so ./
COPY pyproject.toml ./
COPY python ./python

RUN maturin build --release && \
    pip install target/wheels/*.whl

CMD ["python", "-m", "myproject"]
```

## CI/CD 配置

### GitHub Actions

```yaml
name: Build and Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
        python-version: ['3.8', '3.9', '3.10', '3.11']
    
    steps:
    - uses: actions/checkout@v3
    
    - uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - uses: actions-rs/toolchain@v1
      with:
        toolchain: stable
    
    - name: Install maturin
      run: pip install maturin pytest numpy
    
    - name: Build
      run: maturin develop
    
    - name: Test
      run: pytest tests/
```

## 多架構建置

```bash
# x86_64
maturin build --release --target x86_64-unknown-linux-gnu

# ARM64
maturin build --release --target aarch64-unknown-linux-gnu

# macOS Universal
maturin build --release --target universal2-apple-darwin
```

## 發布到 PyPI

```bash
# 建置所有平台的 wheels
maturin build --release --target x86_64-unknown-linux-gnu
maturin build --release --target aarch64-unknown-linux-gnu
maturin build --release --target x86_64-apple-darwin

# 上傳到 PyPI
maturin publish
```
