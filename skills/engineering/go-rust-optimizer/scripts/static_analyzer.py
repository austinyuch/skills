#!/usr/bin/env python3
"""
靜態代碼分析工具：識別適合轉換為 Rust 的 Go 代碼模式
"""

import re
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List

@dataclass
class Hotspot:
    file: str
    line: int
    pattern: str
    reason: str
    severity: str  # HIGH, MEDIUM, LOW

def analyze_go_file(filepath: Path) -> List[Hotspot]:
    """分析單個 Go 檔案"""
    hotspots = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines, 1):
        # Pattern A: 複雜數學運算
        if re.search(r'math\.(Pow|Sqrt|Sin|Cos|Exp|Log)', line):
            hotspots.append(Hotspot(
                file=str(filepath),
                line=i,
                pattern="Complex Math",
                reason="數學運算密集，Rust SIMD 可加速",
                severity="HIGH"
            ))
        
        # Pattern B: 頻繁的 append 操作
        if re.search(r'append\(.*\)', line) and 'for' in ''.join(lines[max(0, i-5):i]):
            hotspots.append(Hotspot(
                file=str(filepath),
                line=i,
                pattern="Loop Append",
                reason="迴圈內頻繁 append，可能導致記憶體重新分配",
                severity="MEDIUM"
            ))
        
        # Pattern C: interface{} 轉換
        if 'interface{}' in line and 'for' in ''.join(lines[max(0, i-5):i]):
            hotspots.append(Hotspot(
                file=str(filepath),
                line=i,
                pattern="Interface Boxing",
                reason="迴圈內 interface{} 轉換，增加 GC 壓力",
                severity="HIGH"
            ))
        
        # Pattern D: 大型結構體拷貝
        if re.search(r'=\s*\w+\{.*\}', line) and len(line) > 100:
            hotspots.append(Hotspot(
                file=str(filepath),
                line=i,
                pattern="Large Struct Copy",
                reason="大型結構體拷貝，Rust 可使用 zero-copy",
                severity="MEDIUM"
            ))
    
    return hotspots

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 static_analyzer.py <go-file-or-directory>")
        sys.exit(1)
    
    target = Path(sys.argv[1])
    
    if target.is_file():
        files = [target]
    elif target.is_dir():
        files = list(target.rglob("*.go"))
    else:
        print(f"❌ Invalid path: {target}")
        sys.exit(1)
    
    all_hotspots = []
    for file in files:
        hotspots = analyze_go_file(file)
        all_hotspots.extend(hotspots)
    
    # 按嚴重性排序
    all_hotspots.sort(key=lambda x: {"HIGH": 0, "MEDIUM": 1, "LOW": 2}[x.severity])
    
    print("=== Static Analysis Results ===\n")
    
    if not all_hotspots:
        print("✅ No obvious optimization candidates found.")
        return
    
    for hotspot in all_hotspots:
        print(f"[{hotspot.severity}] {hotspot.file}:{hotspot.line}")
        print(f"  Pattern: {hotspot.pattern}")
        print(f"  Reason: {hotspot.reason}")
        print()
    
    print(f"Total hotspots found: {len(all_hotspots)}")
    print(f"  HIGH: {sum(1 for h in all_hotspots if h.severity == 'HIGH')}")
    print(f"  MEDIUM: {sum(1 for h in all_hotspots if h.severity == 'MEDIUM')}")
    print(f"  LOW: {sum(1 for h in all_hotspots if h.severity == 'LOW')}")

if __name__ == "__main__":
    main()
