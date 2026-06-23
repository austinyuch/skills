#!/usr/bin/env python3
"""Targeted mutation check for run.py (dependency-free, reproducible).

Applies each mutant to an isolated copy of the skill scripts and runs the test suite against
it; a mutant is KILLED iff the suite turns red. Run: python3 mutation_check.py
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "run.py")

MUTANTS = [
    ("M1 severity-map flip (CRITICAL->low)", '"CRITICAL": "high"', '"CRITICAL": "low"'),
    ("M2 ranking ascending (drop the minus)", 'key=lambda f: (-f["risk_score"]', 'key=lambda f: (f["risk_score"]'),
    ("M3 drop blast multiplier", " * blast, 2)", " * 1, 2)"),
    ("M4 drop type factor", 'TYPE_FACTOR.get(f["type"], 1.0) *', "1.0 *"),
]


def main():
    src = open(SRC).read()
    killed = 0
    for name, old, new in MUTANTS:
        if old not in src:
            print(f"{name}: ANCHOR-NOT-FOUND (test is stale)")
            continue
        d = tempfile.mkdtemp(prefix="mut_")
        try:
            for fn in ("llm_provider.py", "test_run.py"):
                shutil.copy(os.path.join(HERE, fn), os.path.join(d, fn))
            open(os.path.join(d, "run.py"), "w").write(src.replace(old, new, 1))
            r = subprocess.run([sys.executable, os.path.join(d, "test_run.py")],
                               capture_output=True, text=True)
            status = "KILLED" if r.returncode != 0 else "SURVIVED"
            killed += r.returncode != 0
            print(f"{name}: {status}")
        finally:
            shutil.rmtree(d, ignore_errors=True)
    print(f"\n{killed}/{len(MUTANTS)} mutants killed")
    sys.exit(0 if killed == len(MUTANTS) else 1)


if __name__ == "__main__":
    main()
