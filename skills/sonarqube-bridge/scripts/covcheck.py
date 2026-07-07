#!/usr/bin/env python3
"""Dependency-free line-coverage check for run.py using the stdlib trace module.

Exercises the full deterministic core + CLI success/error paths in-process so the
coverage number reflects real behaviour (the api-network branch is the only path left
to integration/live). Prints `COVERAGE <pct>` and the uncovered lines.
"""
import contextlib
import importlib.util
import io
import json
import os
import sys
import tempfile
import trace

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.join(HERE, "run.py")

SAMPLE = [
    {"rule": "go:S2076", "severity": "CRITICAL", "type": "VULNERABILITY", "component": "p:a.go",
     "line": 1, "message": "running this OS command", "tags": ["cwe-78", "owasp-a3"]},
    {"rule": "cs:S3776", "severity": "MAJOR", "type": "CODE_SMELL", "component": "p:b.cs",
     "line": 2, "message": "Cognitive Complexity", "tags": []},
    {"rule": "ts:S1764", "severity": "MINOR", "type": "BUG", "component": "p:c.ts",
     "line": 3, "message": "duplicated sub-expression", "tags": []},
    {"rule": "x:S1", "severity": "INFO", "type": "SECURITY_HOTSPOT", "component": "p:d",
     "line": 4, "message": "review this credential", "tags": []},
    {"rule": "cs:S4", "severity": "MAJOR", "type": "CODE_SMELL", "component": "p:e.cs",
     "line": 5, "message": "This block is duplicated.", "tags": []},
    {"rule": "cs:S5", "severity": "MAJOR", "type": "CODE_SMELL", "component": "p:f.cs",
     "line": 6, "message": "too many parameters", "tags": []},
    {"rule": "cs:S6", "severity": "MINOR", "type": "CODE_SMELL", "component": "p:g.cs",
     "line": 7, "message": "remove unused import", "tags": []},
]


def exercise():
    spec = importlib.util.spec_from_file_location("run", RUN)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.process(SAMPLE, {"a.go": 5}, {"a.go": "Pay"})
    m.process(SAMPLE, {"a.go": "not-a-number"}, {})  # non-numeric blast → default 1.0
    m.map_severity("BLOCKER"); m.map_severity("weird")
    f = [m.normalize_issue(i) for i in SAMPLE]
    m.build_explain_prompt(f)
    m.apply_explanation(f, '{"findings":[{"rule":"go:S2076","line":1,"severity":"high","remediation":"x"}]}')
    fd, p = tempfile.mkstemp(suffix=".json")
    os.write(fd, json.dumps({"issues": SAMPLE}).encode()); os.close(fd)
    fd2, p2 = tempfile.mkstemp(suffix=".json")
    os.write(fd2, json.dumps(SAMPLE).encode()); os.close(fd2)  # bare-list branch
    fd3, p3 = tempfile.mkstemp(suffix=".json")
    os.write(fd3, json.dumps({"not_issues": 1}).encode()); os.close(fd3)  # malformed branch
    argvs = [
        ["run.py", json.dumps({"source": "file", "issues_file": p})],
        ["run.py", json.dumps({"source": "file", "issues_file": p2})],
        ["run.py", json.dumps({}), "--mock"],
        ["run.py", "badjson"],
        ["run.py", json.dumps([1, 2])],                                   # not an object
        ["run.py", json.dumps({"source": "api"})],                        # no host
        ["run.py", json.dumps({"source": "api", "host": "h"})],           # no project
        ["run.py", json.dumps({"source": "api", "host": "h", "project_key": "p"})],  # no token
        ["run.py", json.dumps({"source": "file"})],                       # no file
        ["run.py", json.dumps({"source": "file", "issues_file": "/no/x"})],
        ["run.py", json.dumps({"source": "weird"})],
        ["run.py", json.dumps({"source": "file", "issues_file": p3})],   # malformed -> _issues_of fail
        ["run.py", json.dumps({"source": "file", "issues_file": p}), "--explain"],  # explain fails closed
    ]
    for argv in argvs:
        sys.argv = argv
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            try:
                m.main()
            except SystemExit:
                pass
    os.unlink(p); os.unlink(p2); os.unlink(p3)


t = trace.Trace(count=1, trace=0)
t.runfunc(exercise)
cov = "/tmp/sonarcov_prog"
os.makedirs(cov, exist_ok=True)
t.results().write_results(show_missing=True, summary=False, coverdir=cov)
path = os.path.join(cov, "run.cover")
import re
executed = notexec = 0; miss = []
for ln in open(path):
    if ln.startswith(">>>>>>"):
        notexec += 1; miss.append(ln[8:].rstrip())
    elif re.match(r"\s*\d+:", ln):
        executed += 1
tot = executed + notexec
print(f"COVERAGE {executed}/{tot} = {executed*100//tot}%")
for g in miss:
    print("  UNCOVERED:", g.strip()[:78])
