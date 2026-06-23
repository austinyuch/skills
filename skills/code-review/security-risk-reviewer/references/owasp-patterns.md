# OWASP pattern reference (security reviewer)

Read when explaining a finding or judging a low-confidence flag. Mappings follow the OWASP
Top-10 (2021) and CWE. These are detection heuristics, not proof of a vulnerability —
confirm exploitability before reporting a true positive.

## Injection (A03) — the high-value family
- **SQL injection (CWE-89)** — query built by string concat / f-string / `.format` / `%`.
  Fix: parameterized queries / prepared statements / an ORM binding. The fix is mechanical and
  near-total; flag every occurrence.
- **Command injection (CWE-78)** — `os.system`, `shell=True`, `exec.Command("sh","-c",…)`,
  backticks with interpolated data. Fix: pass argv arrays, drop the shell, allow-list inputs.
- **XSS (CWE-79)** — `innerHTML=`, `dangerouslySetInnerHTML`, `document.write`, `|safe`,
  `v-html`, `render_template_string`. Fix: contextual output encoding, auto-escaping templates,
  sanitize HTML you must render.

## Cryptographic failures (A02)
- **Weak crypto (CWE-327)** — MD5/SHA-1 (especially for passwords), DES, ECB mode,
  `Math.random()` for security tokens. Fix: bcrypt/argon2 for passwords, SHA-256+ for
  integrity, a CSPRNG (`secrets`, `crypto/rand`) for tokens/IDs.

## Identification & auth failures (A07)
- **Hardcoded secret (CWE-798)** — AWS keys (`AKIA…`), GitHub/Slack tokens, PEM private-key
  blocks, `password=/api_key=` literals. Fix: secret manager / env var, and **rotate** anything
  that reached source control — exposure is not undone by deleting the line.

## Software & data integrity failures (A08)
- **Insecure deserialization (CWE-502)** — `pickle.loads`, `yaml.load` without `SafeLoader`,
  `marshal.loads`. Fix: `yaml.safe_load`, JSON, or a schema-validated format; never deserialize
  untrusted input into live objects.

## Security misconfiguration (A05)
- **Disabled TLS verification (CWE-295)** — `verify=False`, `InsecureSkipVerify: true`,
  `rejectUnauthorized: false`. Fix: keep verification on; trust a proper CA / pin a cert rather
  than disabling validation. Common in "make it work" code that ships to prod.

## Broken access control (A01)
- **Path traversal (CWE-22)** — user input flowing into `open`/`filepath.Join`/`sendfile`.
  Fix: canonicalize, reject `..`, resolve against a fixed base directory, allow-list.

## Server-side request forgery (A10)
- **SSRF (CWE-918)** — an HTTP client fetches a URL the caller controls (`requests.get(url)`,
  `urllib.request.urlopen(uri)`, `http.Get(target)`). An attacker can pivot to internal
  services or the cloud metadata endpoint. Fix: allow-list hosts/schemes, block internal/
  link-local/metadata ranges, never fetch a raw user-supplied URL.

## Risk-based prioritization (the point of `risk_ranking`)
`risk_score = severity_weight × confidence × blast_radius`. Review top-down. Two amplifiers:
- **Blast radius** — supply it from the code graph's impact/`developer-routing`: the same
  flaw in a core, widely-imported module is worth more attention than in a leaf script.
- **Confidence** — high-confidence rules (key formats, PEM, `verify=False`) are near-certain;
  low-confidence rules (generic secret/SQL/path patterns) need human or `--explain` triage.

## Boundary
This is a fast triage aid for review, **not** a SAST tool or a release gate. It has no taint
tracking and no dependency-CVE scan; pair it with a dedicated scanner (and this repo's Spec
#79 `npm audit` / Go advisory flow) for gating.
