# 專案結構與建置配置

## 標準目錄結構

```
project/
├── Makefile                # 自動化建置
├── go.mod                  # Go 專案定義
├── main.go                 # 應用邏輯入口
├── sdk.go                  # CGO 宣告與 Rust 函式封裝
├── include/                # Rust 生成的 C Header
│   └── rust_core.h
├── lib/                    # 編譯好的靜態庫
│   └── librust_core.a
└── rust_core/              # Rust 核心運算模組
    ├── Cargo.toml
    ├── cbindgen.toml       # C header 生成配置
    └── src/
        └── lib.rs
```

## Cargo.toml 配置

```toml
[package]
name = "rust_core"
version = "0.1.0"
edition = "2021"

[lib]
# 產生靜態庫 (.a)，適合嵌入式環境
crate-type = ["staticlib"]

[dependencies]
libc = "0.2"

[profile.release]
opt-level = 3           # 最高優化
lto = true              # Link-Time Optimization
codegen-units = 1       # 單一編譯單元，更好的優化
panic = "abort"         # 減少二進位大小
strip = true            # 移除符號表
```

## cbindgen.toml 配置

```toml
language = "C"
braces = "SameLine"
line_length = 80
tab_width = 4
documentation_style = "c99"

[export]
# 指定需要導出到 Go 的結構體
include = ["SensorData", "RustResult"]

[export.rename]
# 重命名以避免衝突
"SensorData" = "RustSensorData"
```

## Makefile 範本

```makefile
RUST_DIR = ./rust_core
LIB_NAME = librust_core.a
TARGET_LIB = ./lib/$(LIB_NAME)
GEN_HEADER = ./include/rust_core.h

# 根據架構選擇 Rust target
ifeq ($(TARGET_ARCH), arm64)
    RUST_TARGET = aarch64-unknown-linux-gnu
    GO_ARCH = arm64
else
    RUST_TARGET = x86_64-unknown-linux-gnu
    GO_ARCH = amd64
endif

.PHONY: all build_rust build_go clean test

all: build_rust build_go

# 1. 生成 C Headers
gen_header:
	@echo "--- Generating C Headers ---"
	mkdir -p ./include
	cbindgen --config $(RUST_DIR)/cbindgen.toml \
	         --crate rust_core \
	         --output $(GEN_HEADER)

# 2. 編譯 Rust 核心
build_rust: gen_header
	@echo "--- Building Rust Core ($(RUST_TARGET)) ---"
	rustup target add $(RUST_TARGET)
	cd $(RUST_DIR) && cargo build --release --target $(RUST_TARGET)
	mkdir -p ./lib
	cp $(RUST_DIR)/target/$(RUST_TARGET)/release/$(LIB_NAME) $(TARGET_LIB)

# 3. 編譯 Go 程式
build_go: build_rust
	@echo "--- Building Go App ---"
	GOOS=linux GOARCH=$(GO_ARCH) CGO_ENABLED=1 \
	go build -ldflags "-linkmode external -extldflags '-static'" -o edge_app .

# 4. 效能測試
test: build_rust
	@echo "--- Running Benchmarks ---"
	go test -v -bench=. -benchmem

# 5. 驗證符號表
verify:
	@echo "--- Verifying Symbols ---"
	nm $(TARGET_LIB) | grep -E "rust_|process_"

clean:
	rm -rf ./lib ./include edge_app
	cd $(RUST_DIR) && cargo clean
```

## Docker Multi-stage Build

```dockerfile
FROM --platform=$BUILDPLATFORM golang:1.22-bookworm AS builder

# 安裝 Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# 安裝 cbindgen
RUN cargo install cbindgen

WORKDIR /app
COPY . .

ARG TARGETARCH
RUN make build_all TARGET_ARCH=$TARGETARCH

# 最終鏡像
FROM debian:bookworm-slim
WORKDIR /root/
COPY --from=builder /app/edge_app .
CMD ["./edge_app"]
```

## 建置命令

```bash
# 本地開發 (x86_64)
make all

# 交叉編譯 ARM64
make all TARGET_ARCH=arm64

# Docker 多架構建置
docker buildx build --platform linux/amd64,linux/arm64 -t myapp:latest .

# 驗證
make verify
```
