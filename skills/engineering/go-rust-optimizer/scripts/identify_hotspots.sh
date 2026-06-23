#!/bin/bash
# 使用 pprof 尋找最耗時的函式

set -e

echo "=== Go Performance Profiling ==="
echo "Running benchmarks with CPU profiling..."

# 執行 benchmark 並產生 CPU profile
go test -bench=. -cpuprofile=cpu.out ./...

# 分析 profile 並輸出前 10 個熱點
echo ""
echo "=== Top 10 CPU Hotspots ==="
go tool pprof -top cpu.out | head -n 15 > hotspots.txt

# 顯示結果
cat hotspots.txt

echo ""
echo "✅ Hotspot analysis saved to hotspots.txt"
echo ""
echo "Candidates for Rust optimization:"
echo "- Functions with >15% CPU usage"
echo "- Tight loops with heavy computation"
echo "- Frequent memory allocations"
