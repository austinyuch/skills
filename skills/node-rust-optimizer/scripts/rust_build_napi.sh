#!/bin/bash

# NAPI-RS 建置腳本
# 用法: ./rust_build_napi.sh [rust_dir] [target_arch]

set -e

RUST_DIR=${1:-.}
TARGET_ARCH=${2:-$(uname -m)}

echo "🦀 開始建置 NAPI-RS 模組"
echo "📁 Rust 目錄: $RUST_DIR"
echo "🎯 目標架構: $TARGET_ARCH"

cd "$RUST_DIR"

# 檢查必要檔案
if [ ! -f "Cargo.toml" ]; then
    echo "❌ 錯誤: 找不到 Cargo.toml"
    exit 1
fi

if [ ! -f "package.json" ]; then
    echo "❌ 錯誤: 找不到 package.json"
    exit 1
fi

# 安裝 Node.js 依賴
echo "📦 安裝 Node.js 依賴..."
npm install

# 根據架構設定目標
case "$TARGET_ARCH" in
    x86_64|amd64)
        RUST_TARGET="x86_64-unknown-linux-gnu"
        ;;
    aarch64|arm64)
        RUST_TARGET="aarch64-unknown-linux-gnu"
        ;;
    *)
        echo "⚠️  未知架構 $TARGET_ARCH，使用預設目標"
        RUST_TARGET=""
        ;;
esac

# 建置
echo "🔨 建置 Rust 模組..."
if [ -n "$RUST_TARGET" ]; then
    echo "   目標: $RUST_TARGET"
    rustup target add "$RUST_TARGET" 2>/dev/null || true
    npm run build -- --target "$RUST_TARGET"
else
    npm run build
fi

# 檢查輸出
if [ -f "*.node" ]; then
    echo "✅ 建置成功！"
    ls -lh *.node
else
    echo "❌ 建置失敗：找不到 .node 檔案"
    exit 1
fi

# 產生 TypeScript 定義
if [ -f "index.d.ts" ]; then
    echo "✅ TypeScript 定義已產生"
else
    echo "⚠️  警告: 未找到 TypeScript 定義檔"
fi

echo ""
echo "🎉 建置完成！"
echo ""
echo "下一步:"
echo "  1. 執行測試: npm test"
echo "  2. 執行基準測試: npm run bench"
echo "  3. 整合到專案: npm install $RUST_DIR"
