---
name: python-rust-optimizer
description: Python 效能瓶頸識別與 Rust 重構自動化工具。當需要優化 Python 專案效能、識別計算密集型熱點、將高負載迴圈轉換為 Rust PyO3 擴展、支援 NumPy zero-copy、釋放 GIL 實現真正並行、或在資料科學/機器學習/影像處理場景中達到極致效能時使用。適用於 NumPy 密集運算、資料處理管線、即時系統、科學計算等高效能場景。
---

# Python-to-Rust Performance Engineer

## 概述

此 skill 提供系統化的 Python 效能優化流程，透過識別計算密集型熱點並使用 Rust PyO3 擴展進行局部重構，達到極致的執行效率。特別適合資料科學、機器學習和高效能計算場景。


## 核心原則

### GIL-Free 優先
使用 `py.allow_threads()` 釋放 GIL，實現真正的並行處理，特別適合 CPU 密集型運算。

### NumPy Zero-Copy
使用 `numpy` crate 的 `PyReadonlyArray` 直接操作 NumPy 記憶體，避免資料複製開銷。

### Rayon 並行化
利用 Rayon 進行資料並行處理，充分利用多核心 CPU。

### 最小邊界跨越
批次處理資料以減少 Python/Rust 邊界跨越次數，降低開銷。

## 工作流程

### 階段 1: 識別與剖析 (Profiling & Analysis)

**目標**: 使用 cProfile 和靜態分析識別效能瓶頸。

**執行步驟**:

1. **動態分析**: 執行 `scripts/identify_hotspots.py <script.py>`
   - 使用 cProfile 產生效能報告
   - 識別累積時間佔比高的函式
   - 找出 CPU 密集型運算

2. **靜態分析**: 執行 `scripts/static_analyzer.py <directory>`
   - 掃描迴圈內的 NumPy 運算
   - 識別 list comprehension 在迴圈內
   - 標記頻繁的 list.append 操作
   - 檢測數學運算密集區塊

3. **決策評估**: 參考 `references/decision_matrix.md`
   - 評估資料大小 (< 1KB 保留 Python, > 100KB 使用 Rust)
   - 評估累積時間 (> 20% 強烈建議 Rust)
   - 評估 GIL 影響 (CPU 密集型建議 Rust)

**識別規則**:
- **高優先級**: NumPy 密集運算、純 Python 迴圈、並行需求
- **中優先級**: List comprehension (大資料)、字串處理
- **低優先級**: I/O 操作、網路請求、簡單業務邏輯

### 階段 2: Rust 擴展開發 (PyO3 Extension Development)

**目標**: 使用 PyO3 建立高效能 Rust 擴展。

**技術要求**:
- 使用 PyO3 `#[pyfunction]` 和 `#[pyclass]` 導出
- NumPy 陣列使用 `PyReadonlyArray` 實現 zero-copy
- CPU 密集型運算使用 `py.allow_threads()` 釋放 GIL
- 並行處理使用 Rayon

**實作步驟**:

1. **建立專案結構**:
   ```bash
   mkdir -p src
   cp assets/Cargo.toml.template Cargo.toml
   cp assets/pyproject.toml.template pyproject.toml
   cp assets/lib.rs.template src/lib.rs
   ```

2. **實作 Rust 函式**: 參考 `references/pyo3_patterns.md`
   - 簡單函式: `#[pyfunction]`
   - NumPy 處理: `PyReadonlyArray1<T>`
   - 並行處理: `py.allow_threads()` + Rayon
   - 類別導出: `#[pyclass]` + `#[pymethods]`

3. **錯誤處理**:
   - 使用 `PyResult<T>` 回傳結果
   - 使用 `PyErr` 拋出 Python 異常

### 階段 3: 建置與整合 (Build & Integration)

**目標**: 使用 Maturin 建置並整合到 Python 專案。

**實作步驟**:

1. **安裝 Maturin**:
   ```bash
   pip install maturin
   ```

2. **開發模式建置**: 執行 `scripts/rust_build_extension.sh [rust_dir] [arch]`
   - 自動偵測或指定目標架構
   - 使用 `maturin develop` 快速迭代
   - 自動安裝到當前 Python 環境

3. **發布模式建置**:
   ```bash
   maturin build --release
   pip install target/wheels/*.whl
   ```

4. **專案結構**: 參考 `references/project_structure.md`
   - 標準 PyO3 專案佈局
   - Maturin 配置
   - 測試與 benchmark 設定

### 階段 4: 測試與基準測試 (Testing & Benchmarking)

**目標**: 確保邏輯正確並量化效能增益。

**測試步驟**:

1. **一致性測試**:
   ```python
   def test_consistency():
       data = [1.0, 2.0, 3.0, 4.0]
       py_result = python_sum(data)
       rust_result = rust_ext.sum_array(data)
       assert abs(py_result - rust_result) < 1e-6
   ```

2. **NumPy 測試**:
   ```python
   def test_numpy():
       data = np.array([1.0, 2.0, 3.0], dtype=np.float64)
       result = rust_ext.process_numpy(data)
       expected = np.array([2.0, 4.0, 6.0])
       np.testing.assert_array_almost_equal(result, expected)
   ```

3. **效能基準測試**:
   ```python
   import time
   
   def benchmark():
       data = np.random.rand(1000000)
       
       start = time.time()
       py_result = python_process(data)
       py_time = time.time() - start
       
       start = time.time()
       rust_result = rust_ext.process_numpy(data)
       rust_time = time.time() - start
       
       print(f"Speedup: {py_time/rust_time:.2f}x")
   ```

**預期結果**:
- NumPy 密集運算: 2-5x 加速
- 純 Python 迴圈: 10-100x 加速
- 並行處理: 4-8x 加速

## 多架構支援

### 支援平台
- Linux: x86_64, aarch64
- macOS: x86_64, aarch64 (Apple Silicon)
- Windows: x86_64

### 建置命令

```bash
# 本地開發
maturin develop

# 特定架構
maturin build --release --target x86_64-unknown-linux-gnu
maturin build --release --target aarch64-unknown-linux-gnu

# macOS Universal
maturin build --release --target universal2-apple-darwin
```

## PyPI 發布

```bash
# 建置所有平台 wheels
maturin build --release --target x86_64-unknown-linux-gnu
maturin build --release --target aarch64-unknown-linux-gnu
maturin build --release --target x86_64-apple-darwin

# 上傳到 PyPI
maturin publish
```

## 完成定義 (Definition of Done)

- ✅ 效能分析: 已執行 cProfile 並識別瓶頸
- ✅ 靜態分析: 已掃描並標記優化候選
- ✅ 一致性測試: Python 與 Rust 結果一致
- ✅ 效能驗證: 達到預期加速比
- ✅ NumPy 整合: Zero-copy 正確實作
- ✅ GIL 管理: CPU 密集型已釋放 GIL
- ✅ 錯誤處理: 使用 PyResult 正確處理錯誤

## 參考資料

詳細技術細節請參考：
- `references/pyo3_patterns.md` - PyO3 模式與最佳實踐
- `references/project_structure.md` - 專案結構與建置配置
- `references/decision_matrix.md` - 決策矩陣：何時使用 Rust 優化

## 範例使用

```bash
# 1. 識別熱點
python3 scripts/identify_hotspots.py my_script.py
python3 scripts/static_analyzer.py ./myproject

# 2. 建立 Rust 擴展
mkdir -p src
cp assets/*.template .

# 3. 實作 Rust 函式 (參考 references/pyo3_patterns.md)

# 4. 建置與測試
./scripts/rust_build_extension.sh . x86_64
pytest tests/

# 5. 發布
maturin build --release
pip install target/wheels/*.whl
```

## Python 特定優勢

### vs NumPy
- 更細粒度的控制
- 自定義 SIMD 優化
- 更好的記憶體管理

### vs Cython
- 更好的型別安全
- 更現代的語法
- 更好的錯誤訊息
- 無需 C 編譯器知識

### vs C Extensions
- 記憶體安全保證
- 更簡潔的程式碼
- 更好的開發體驗
- 自動參照計數管理
