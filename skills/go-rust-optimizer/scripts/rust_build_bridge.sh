#!/bin/bash
# 自動編譯 Rust 並將庫移動到 Go 專案目錄

set -e

RUST_DIR=${1:-"rust_core"}
TARGET_ARCH=${2:-$(uname -m)}

echo "=== Building Rust Core for $TARGET_ARCH ==="

# 確定 Rust target
case $TARGET_ARCH in
    x86_64|amd64)
        RUST_TARGET="x86_64-unknown-linux-gnu"
        ;;
    aarch64|arm64)
        RUST_TARGET="aarch64-unknown-linux-gnu"
        ;;
    *)
        echo "❌ Unsupported architecture: $TARGET_ARCH"
        exit 1
        ;;
esac

echo "Rust target: $RUST_TARGET"

# 添加 target (如果尚未安裝)
rustup target add $RUST_TARGET

# 編譯 Rust
cd $RUST_DIR
cargo build --release --target $RUST_TARGET

# 建立 lib 目錄
cd ..
mkdir -p lib

# 複製靜態庫
LIB_NAME="librust_core.a"
cp $RUST_DIR/target/$RUST_TARGET/release/$LIB_NAME lib/

echo "✅ Rust library built and copied to lib/$LIB_NAME"

# 生成 C header (如果有 cbindgen)
if command -v cbindgen &> /dev/null; then
    echo "Generating C headers..."
    mkdir -p include
    cbindgen --config $RUST_DIR/cbindgen.toml --crate rust_core --output include/rust_core.h
    echo "✅ C headers generated at include/rust_core.h"
fi

# 設定環境變數
export CGO_LDFLAGS="-L./lib -lrust_core -ldl -lpthread -lm"
echo ""
echo "Environment variable set:"
echo "export CGO_LDFLAGS=\"$CGO_LDFLAGS\""
