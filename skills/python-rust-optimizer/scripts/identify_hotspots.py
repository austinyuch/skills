#!/usr/bin/env python3
"""
Python 效能分析工具：使用 cProfile 和 line_profiler 識別熱點
"""

import cProfile
import pstats
import io
import sys
from pathlib import Path

def profile_script(script_path: str, output_file: str = "hotspots.txt"):
    """執行 Python 腳本並產生效能分析報告"""
    
    print("=== Python Performance Profiling ===")
    print(f"Profiling: {script_path}")
    
    # 執行 cProfile
    profiler = cProfile.Profile()
    
    try:
        with open(script_path) as f:
            code = compile(f.read(), script_path, 'exec')
            profiler.enable()
            exec(code, {'__name__': '__main__'})
            profiler.disable()
    except Exception as e:
        print(f"❌ Error running script: {e}")
        return
    
    # 分析結果
    s = io.StringIO()
    stats = pstats.Stats(profiler, stream=s)
    stats.sort_stats('cumulative')
    stats.print_stats(20)
    
    result = s.getvalue()
    
    # 儲存到檔案
    with open(output_file, 'w') as f:
        f.write(result)
    
    print(f"\n✅ Profile saved to {output_file}")
    print("\n=== Top 10 Hotspots ===")
    
    # 顯示前 10 個熱點
    lines = result.split('\n')
    for line in lines[:30]:
        print(line)
    
    print("\nCandidates for Rust optimization:")
    print("- Functions with high cumulative time")
    print("- Tight loops with numerical computation")
    print("- List comprehensions with heavy processing")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 identify_hotspots.py <python-script>")
        sys.exit(1)
    
    profile_script(sys.argv[1])
