#!/usr/bin/env python3
"""
靜態代碼分析：識別適合轉換為 Rust 的 Python 代碼模式
"""

import ast
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
    severity: str

class HotspotAnalyzer(ast.NodeVisitor):
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.hotspots: List[Hotspot] = []
        self.in_loop = False
        self.loop_depth = 0
    
    def visit_For(self, node):
        self.in_loop = True
        self.loop_depth += 1
        self.generic_visit(node)
        self.loop_depth -= 1
        if self.loop_depth == 0:
            self.in_loop = False
    
    def visit_While(self, node):
        self.in_loop = True
        self.loop_depth += 1
        self.generic_visit(node)
        self.loop_depth -= 1
        if self.loop_depth == 0:
            self.in_loop = False
    
    def visit_ListComp(self, node):
        # List comprehension 在迴圈內
        if self.in_loop and len(node.generators) > 0:
            self.hotspots.append(Hotspot(
                file=self.filepath,
                line=node.lineno,
                pattern="Nested List Comprehension",
                reason="迴圈內的 list comprehension，可能導致大量記憶體分配",
                severity="HIGH"
            ))
        self.generic_visit(node)
    
    def visit_Call(self, node):
        # NumPy/數學運算
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                module = node.func.value.id
                if module in ['np', 'numpy', 'math']:
                    if self.in_loop:
                        self.hotspots.append(Hotspot(
                            file=self.filepath,
                            line=node.lineno,
                            pattern="Numerical Computation in Loop",
                            reason=f"迴圈內的 {module} 運算，Rust 可提供 SIMD 加速",
                            severity="HIGH"
                        ))
        
        # append 在迴圈內
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == 'append' and self.in_loop:
                self.hotspots.append(Hotspot(
                    file=self.filepath,
                    line=node.lineno,
                    pattern="List Append in Loop",
                    reason="迴圈內頻繁 append，可能導致 list 重新分配",
                    severity="MEDIUM"
                ))
        
        self.generic_visit(node)
    
    def visit_BinOp(self, node):
        # 數學運算在迴圈內
        if self.in_loop and isinstance(node.op, (ast.Mult, ast.Div, ast.Pow, ast.MatMult)):
            self.hotspots.append(Hotspot(
                file=self.filepath,
                line=node.lineno,
                pattern="Math Operation in Loop",
                reason="迴圈內的數學運算，Rust 可優化",
                severity="MEDIUM"
            ))
        self.generic_visit(node)

def analyze_file(filepath: Path) -> List[Hotspot]:
    """分析單個 Python 檔案"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=str(filepath))
        
        analyzer = HotspotAnalyzer(str(filepath))
        analyzer.visit(tree)
        return analyzer.hotspots
    except Exception as e:
        print(f"⚠️  Error analyzing {filepath}: {e}")
        return []

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 static_analyzer.py <python-file-or-directory>")
        sys.exit(1)
    
    target = Path(sys.argv[1])
    
    if target.is_file():
        files = [target]
    elif target.is_dir():
        files = list(target.rglob("*.py"))
    else:
        print(f"❌ Invalid path: {target}")
        sys.exit(1)
    
    all_hotspots = []
    for file in files:
        hotspots = analyze_file(file)
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
