#!/bin/bash
# 自動編譯 Rust PyO3 擴展並安裝

set -e

RUST_DIR=${1:-"rust_ext"}
TARGET_ARCH=${2:-$(uname -m)}

echo "=== Building Rust PyO3 Extension for $TARGET_ARCH ==="

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

# 檢查 maturin 是否安裝
if ! command -v maturin &> /dev/null; then
    echo "Installing maturin..."
    pip install maturin
fi

# 添加 target
rustup target add $RUST_TARGET

# 進入 Rust 目錄
cd $RUST_DIR

# 使用 maturin 建置
echo "Building with maturin..."
maturin build --release --target $RUST_TARGET

# 安裝到當前 Python 環境
echo "Installing extension..."
maturin develop --release

cd ..

echo "✅ Rust extension built and installed successfully"
echo ""
echo "Test with:"
echo "  python3 -c 'import rust_ext; print(rust_ext.__doc__)'"
