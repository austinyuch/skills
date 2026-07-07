# Command Notes

This file is the **operator cookbook** for a generic agent. Use it when the plain command list in `SKILL.md` is not enough to decide what to run next.

Read `skill-integration.md` when the current workspace is the `aclab-uat-demo-agent` source repo and the request also touches spec/governance/manual/review surfaces.

Use `python3 scripts/prove_global_skill_cooperation_alignment.py` when you need a bounded workstation proof that:

- global `spec-master` is aligned between `~/.codex/skills/` and `~/.config/opencode/skills/`
- global `spec-driven-development` is aligned between `~/.codex/skills/` and `~/.config/opencode/skills/`
- the repo-owned `uat-demo-agent` cooperation files match the installed bundles in the productized roots

## CLI surfaces

### plan validate

Validates a plan file through the repository's contract + registry path.

Use when you already have a concrete `plan.json` and want the fastest safe check before execution.

### run demo

Runs the demo pipeline and prints structured output containing:

- `Report`
- `Artifacts`
- `Script`

Use when the plan is demo-oriented and you want demo-script output instead of the normal web UAT runner path.

### run uat

Runs the web runner path and prints structured output containing:

- `RunRecord`
- `Artifacts`

Use when the plan is web-oriented. Unless another spec explicitly routes into Windows executor work, this is the normal local UAT path.

### run windows-vm-computer-use

Runs a saved Windows scenario through the execution coordinator as a `targetPlatform=windows-vm` UAT plan and prints structured output containing:

- `runRecord`
- `artifacts`
- `reportPath`
- `bundlePath`

Use when the user or active spec explicitly asks for Windows VM computer-use proof. This is the stable operator entrypoint for a real VM run, but it is not a live-readiness claim until executed against an actual VM and read back through the generated bundle.

Use `--vm-instance <domain-or-instance>` to point the proof command at a known existing VM lifecycle instance/domain. Use `UATDEMO_WINDOWS_VM_INSTANCE` when the same hint should apply to `run uat` Windows VM plans or when the proof command omits the flag. For Cluster A Method 1 live proof, start `scripts/windows-vm-agent.ps1` inside the logged-in Windows desktop session first, then pass `--sidecar-attachment-mode dedicated-agent` or set `UATDEMO_WINDOWS_VM_SIDECAR_ATTACHMENT_MODE=dedicated-agent`; this enforces the intended chain `host -> WinRM file channel -> Windows desktop logged-in-session agent -> UIA + screenshot`, routing UI interaction through the session-resident VM agent instead of guest-local WinRM desktop discovery. When the Windows desktop agent is already running, also pass `--pre-attached-agent` or set `UATDEMO_WINDOWS_VM_PRE_ATTACHED_AGENT=1`; this skips lifecycle bootstrap/readiness advancement and lets the dedicated-agent health file prove readiness over the WinRM file channel.

### report show

Reads a report JSON file and prints a compact human-readable summary.

Use after `run uat` or `run demo` when you want a compact textual readback of the generated report.

## Expected inputs

- Plan files should conform to `contract/plan-definition.schema.json`
- Report files should conform to `contract/report.schema.json`

## Binary and state resolution

### Binary resolution order

1. `UATDEMO_BIN`
2. global config `UATDEMO_BIN`
3. bundled platform binary under `scripts/`
4. `uatdemo` from `PATH`

### State resolution order

1. `UATDEMO_STATE_DIR`
2. project config
3. global config

If the resolved state is project-local, the target project must ignore it in `.gitignore` (`.uatdemo/` or `temp/...`).

## Minimal operating recipes

### A. Validate an existing plan

```bash
${UATDEMO_BIN:-uatdemo} plan validate --file temp/uat-live-plan.json
```

Expected result: JSON with `planId`, `status`, and `version`.

### B. Run a bounded local web UAT smoke

```bash
UATDEMO_STATE_DIR="$PWD/temp/uat-live-state" ${UATDEMO_BIN:-uatdemo} run uat --file temp/uat-live-plan.json
```

Expected result: structured output containing at least:

- `runRecord`
- `reportPath`
- `bundlePath` or report/bundle information
- `artifacts`

### C. Read back the generated report

```bash
UATDEMO_STATE_DIR="$PWD/temp/uat-live-state" ${UATDEMO_BIN:-uatdemo} report show --file temp/uat-live-state/reports/uat-live-example-smoke-uat-report.json
```

Expected result: a compact text summary naming the report and step/artifact information.

### C2. Run a bounded Windows VM computer-use proof

Use this only when the operator has a real VM runtime available for the default `uatdemo` lifecycle-backed VM runner. For the live Windows Calculator closeout, start the dedicated VM agent inside the logged-in desktop session before invoking the host command. Prefer non-terminal scenarios for this proof; do not use shell-launch / terminal-opening scenarios unless a spec explicitly requires approval-gated safety validation.

```bash
OPENCODE_LOCAL_INFRA_ROOT="$PWD/temp/local-infra-registry" UATDEMO_STATE_DIR="$PWD/temp/uat-vm-state" ${UATDEMO_BIN:-uatdemo} run windows-vm-computer-use --file .agents/specs/uat-demo-computer-use-environment-contract/code/scenarios/windows-vm-calculator-smoke.json --vm-instance win11-eval-validation-v8 --sidecar-attachment-mode dedicated-agent --pre-attached-agent
```

Expected result: structured output containing `runRecord`, `reportPath`, `bundlePath`, and `artifacts`.

After the command returns, read the bundle back before making any claim:

```bash
UATDEMO_STATE_DIR="$PWD/temp/uat-vm-state" ${UATDEMO_BIN:-uatdemo} report show --bundle <bundlePath-from-run-output>
```

Do not describe this as live VM readiness unless the command actually ran against a real VM with the dedicated agent active in the logged-in desktop session and the bundle shows the expected `windows-vm` computer-use environment. For a full visual-evidence claim, the host must also have the WinRM file-channel credential (`WINRM_PASSWORD`) set and the bundle/readback must include materialized local screenshot bytes rather than only VM-side `windows-vm://` refs. The VM instance hint, pre-attached hint, and dedicated-agent mode only select the target/channel; they are not evidence by themselves.

### C3. Prove packaged computer-use consumer readback

Use this from the `aclab-uat-demo-agent` source repo when maintainers need a bounded consumer-facing proof that the packaged skill guidance and `uatdemo report show --bundle` read back computer-use evidence. This proof does not execute a VM and does not upgrade live-readiness claims.

```bash
python3 scripts/prove_computer_use_consumer_readback.py --work-dir temp/computer-use-consumer-proof
```

Expected result: JSON with `status: ok`, skill/cookbook marker checks, a generated proof bundle path, and `reportShowOutput` containing `Computer-use environments: 1`.

### C4. Prove a real web computer-use runtime bundle

Use this from the `aclab-uat-demo-agent` source repo when maintainers need a bounded strict proof that `run uat` can produce screenshot-backed computer-use evidence against a real web runtime. The default proof starts a loopback local HTTP target and does not prove Windows VM or arbitrary external/GTO target readiness.

```bash
python3 scripts/prove_external_computer_use_runtime_bundle.py --work-dir temp/external-computer-use-runtime-proof
```

Expected result: JSON with `status: ok`, a generated bundle path, `bundleChecks` showing `coverage`, `readiness`, and `screenshot bytes` as `ok`, `verifierStatus: ok`, and `computerUseEnvironmentCount: 1`.

Use the non-loopback proof when validating that the web runtime evidence path is not localhost-only:

```bash
npm run prove:external-computer-use-nonloopback-runtime-bundle -- --work-dir temp/external-computer-use-nonloopback-runtime-proof
```

Expected result: JSON with `targetHostClass: non-loopback`, a non-loopback `targetUrl`, `bundleChecks` including `screenshot bytes: ok`, and `verifierStatus: ok`. This still does not prove an arbitrary external/GTO target unless the supplied target is that actual environment.

Use the built-in multi-capture proof when validating that the web runtime path can capture multiple distinct routes and fail closed on duplicate screenshot bytes:

```bash
npm run prove:external-computer-use-multicapture-runtime-bundle -- --work-dir temp/external-computer-use-multicapture-runtime-proof
```

Expected result: JSON with `captureCount: 2`, `minUniqueScreenshots: 2`, `bundleChecks` including `screenshot uniqueness: ok`, `verifierStatus: ok`, and `computerUseEnvironmentCount: 2`. This is a repo-local runtime regression proof; it does not prove an arbitrary external/GTO target unless the supplied target is that actual environment.

Use the authenticated built-in multi-capture proof when validating that a login step can establish browser auth state before multiple protected-route captures:

```bash
npm run prove:external-computer-use-auth-multicapture-runtime-bundle -- --work-dir temp/external-computer-use-auth-multicapture-runtime-proof
```

Expected result: JSON with `loginStepIncluded: true`, `planRedacted: true`, retained-plan login redaction `ok`, `captureCount: 2`, `minUniqueScreenshots: 2`, `bundleChecks` including `screenshot uniqueness: ok`, `verifierStatus: ok`, and `computerUseEnvironmentCount: 3` for login plus two protected captures. This is still a repo-local runtime regression proof; actual external/GTO closeout requires the target-url or target-config-file mode against that environment.

Use target-url mode for an actual external/GTO environment:

```bash
npm run prove:external-computer-use-target-url-bundle -- \
  --target-url <https://target.example/path> \
  --ready-selector <css-ready-selector> \
  --capture-selector <css-capture-selector> \
  --work-dir temp/external-computer-use-target-url-proof
```

Expected result: JSON with `targetHostClass: hostname` or `non-loopback`, `targetUrlCount`, `targetHostClasses`, `operatorValueRedaction`, `operatorPathRedaction`, `bundlePathProvided`, `reportPathProvided`, `bundleChecks` including `screenshot bytes: ok`, and `verifierStatus: ok`. It does not echo raw operator target URL, host, target URL list, workdir, state dir, plan path, bundle path, or report path values. Loopback targets are rejected in this mode because the npm entrypoint passes `--require-non-loopback-target`, and host-posture rejection errors do not echo raw host or port values.

For authenticated targets, add the login step and keep secrets out of shell history by using environment-backed values:

```bash
GTO_PASSWORD=<redacted> GTO_APPROVAL_TOKEN=<redacted> \
npm run prove:external-computer-use-target-url-bundle -- \
  --target-url <https://target.example/dashboard> \
  --ready-selector <css-ready-selector> \
  --capture-selector <css-capture-selector> \
  --login-url <https://target.example/login> \
  --login-field '#email=<operator-user>' \
  --login-field '#password=env:GTO_PASSWORD' \
  --login-submit-selector <css-submit-selector> \
  --login-success-url-not-contains /login \
  --approval-token-env GTO_APPROVAL_TOKEN \
  --work-dir temp/external-computer-use-target-url-proof
```

Expected result: JSON with `loginStepIncluded: true`, `planRedacted: true`, `planHygieneChecks` showing retained-plan login redaction `ok`, and operator-target summary fields such as `targetUrlCount`, `targetHostClass`, `targetHostClasses`, `operatorValueRedaction`, `operatorPathRedaction`, `bundlePathProvided`, and `reportPathProvided`; it does not echo raw operator target URL, host, workdir, state dir, plan path, bundle path, or report path values. The login environment may be `hybrid/PASS` without screenshot artifacts, while the capture environment must still provide readable PNG screenshot bytes for strict full-integration closeout.

For repeated external/GTO proof runs, prefer a config file that stores target selectors and environment-variable names, not secret values. The source repo includes an example at `.agents/specs/uat-demo-computer-use-environment-contract/code/external-target-config.example.json`, and the machine-readable shape is tracked at `contract/external-computer-use-target-config.schema.json`. The config file can list multiple `captures[]` for protected-route segments and `minUniqueScreenshots` so strict closeout fails if multiple captures produce duplicate screenshot bytes, such as repeated login-page captures. When `captures[]` is present, put `targetUrl` on each capture and do not also set a top-level `targetUrl`.

Before touching the target, validate the config and required environment variables without launching a browser or running UAT:

```bash
npm run validate:external-computer-use-target-config -- \
  --target-config-file .agents/specs/uat-demo-computer-use-environment-contract/code/external-target-config.example.json
```

Expected result: JSON with `status: ok`, `mode: target-config-schema`, the schema id, capture/login aggregate counts, credential-like/env-backed field counts, and redaction markers. This is schema plus bounded semantic validation: it rejects credential-like login selectors with inline values, including password/token/OTP/MFA/passcode/PIN-style labels, malformed env refs, embedded URL credentials/userinfo, unsupported URL schemes, credential-like URL query/fragment parameters, nested URL credentials, success-condition URL credentials, duplicate capture step IDs, duplicate capture tuples, impossible uniqueness thresholds, duplicate login selectors, credential-like login fields missing approval-token env wiring, and whitespace-only operator strings, but does not resolve environment variables, run browser/UAT, invoke the verifier, or prove external/GTO readiness. Failure output reports only error counts and schema/semantic keywords, not raw target URLs, URL schemes, hosts, routes, selectors, capture step IDs, credential parameter labels, env var names, config key labels, file paths, or secret-like values.

```bash
GTO_PASSWORD=<redacted> GTO_APPROVAL_TOKEN=<redacted> \
npm run prove:external-computer-use-target-config-preflight -- \
  --target-config-file .agents/specs/uat-demo-computer-use-environment-contract/code/external-target-config.example.json
```

Expected result: JSON with `status: ok`, `mode: target-config-preflight`, `targetConfigFileProvided`, `targetUrlCount`, `captureCount`, `captureStepIdCount`, `targetHostClasses`, `loginHostClass`, `loginFieldCount`, `loginEnvBackedFieldCount`, `loginCredentialLikeFieldCount`, `approvalTokenProvided`, `approvalTokenSource`, `loginSuccessConditionKeys`, `operatorValueRedaction`, and `operatorPathRedaction`; it does not echo raw target URLs, target hosts, capture step IDs, login host, login selectors, env var names, or target-config file paths. The preflight rejects missing, blank, or whitespace-only env-backed secrets, ambiguous top-level `targetUrl` when `captures[]` is present, unsupported target-config keys, duplicate capture `stepId` values, duplicate capture target/selector tuples, duplicate login field selectors, malformed or loopback login URLs under external posture, embedded target/login URL credentials or userinfo, common credential-like URL query or fragment parameters, nested redirect/next URL values with embedded credentials or credential-like query/fragment parameters, success-condition credential-like URL query/fragment values, inline `--approval-token` values, inline credential-like `--login-field` values, blank or whitespace-only operator inputs, blank or whitespace-only login field values, blank or whitespace-only env-backed approval-token values, impossible `minUniqueScreenshots` thresholds, and credential-like login fields without approval token before a real run; malformed URL, credential-like URL query/fragment failures, nested URL credential failures, unsupported config-key failures, non-loopback host posture failures, missing/blank env-backed login or approval-token failures, duplicate capture step/tuple, duplicate login selector, missing-approval credential selector, missing/unreadable/malformed target-config file, and preflight success summaries do not echo raw operator URLs, hosts, ports, routes, selectors, config key labels, capture step IDs, credential parameter labels, env var names, paths, config content, or secrets. This is only a preflight; it does not verify bundle evidence or prove external/GTO readiness.

```bash
npm run prove:external-computer-use-target-url-bundle -- \
  --target-config-file .agents/specs/uat-demo-computer-use-environment-contract/code/external-target-config.example.json \
  --work-dir temp/external-computer-use-target-url-proof
```

Set the referenced environment variables, for example `GTO_PASSWORD` and `GTO_APPROVAL_TOKEN`, outside the config file before running the command. The config-file and CLI paths reject duplicate login field selectors, embedded target/login URL credentials or userinfo, common credential-like URL query or fragment parameters, nested redirect/next URL values with embedded credentials or credential-like query/fragment parameters, success-condition credential-like URL query/fragment values, inline approval-token values, blank or whitespace-only approval-token env names/values, credential-like inline field values including OTP/MFA/passcode/PIN-style labels, blank or whitespace-only capture selectors, and blank or whitespace-only login field values; use `--approval-token-env`, `approvalTokenEnv`, `env:NAME`, and `valueEnv` so approval/password/MFA secrets stay outside shell history, process arguments, tracked artifacts, and late browser-login failures. During execution the generated plan briefly contains the resolved login values so `run uat` can authenticate, then the proof script rewrites the retained `planPath` with login field values and approval token redacted and verifies that with `planHygieneChecks`. Operator-supplied actual target proof output emits counts/classes/path-availability booleans/redaction markers instead of raw target URL, target host, target URL list, workdir, state dir, plan path, bundle path, or report path; non-loopback host posture failures do not echo raw host or port values, credential-like URL query/fragment failures do not echo raw parameter labels, and missing/blank env-backed login or approval-token failures do not echo raw env var names. If `run uat` or strict verification fails, prints non-JSON output, returns malformed child-controlled bundle/verifier payload values, points at an unreadable/non-JSON child bundle, or returns malformed nested bundle object/array shapes in operator-target mode, the proof reports exit/parse/contract/read category plus byte counts, value types, error type, JSON line/column, or contract path and redacts raw child output, paths, bundle content, and payload values from the message. If the config has multiple captures and no explicit `--min-unique-screenshots`, the proof requires one distinct readable screenshot byte hash per capture, passes that threshold to packaged `report verify-computer-use-bundle --min-unique-screenshots`, and rejects verifier output that does not report `status: ok`, enough persisted `computerUseEnvironmentCount`, or the configured uniqueness echo/count.

### C5. Verify an external computer-use bundle

Use this when an external target-runtime or another operator returns a candidate computer-use evidence bundle. Strict mode is the closeout gate: it fails if the bundle has no persisted `computerUseEnvironments`, no safety policy/readiness metadata, manual-only source, missing/unreadable screenshot bytes for full-integration evidence, configured screenshot uniqueness is not met, `not_assessed` coverage, `DEMO_NOT_ASSESSED`, or unreadable `report show --bundle` output.

```bash
${UATDEMO_BIN:-uatdemo} report verify-computer-use-bundle --bundle <external-bundle.json>
```

For protected-route multi-capture bundles, pass the same uniqueness threshold expected by the target config so repeated login/fallback-page screenshots fail closeout:

```bash
${UATDEMO_BIN:-uatdemo} report verify-computer-use-bundle --bundle <external-bundle.json> --min-unique-screenshots 2
```

Use handoff/readback mode only to record a conservative blocked or not-assessed bundle without closing Cluster B:

```bash
${UATDEMO_BIN:-uatdemo} report verify-computer-use-bundle --bundle <external-bundle.json> --allow-not-assessed
```

Expected strict closeout result: JSON with `status: ok`, `computerUseEnvironmentCount` greater than zero, `uniqueScreenshotCount` meeting any supplied `minUniqueScreenshots`, and `reportShowOutput` containing `Computer-use environments: <n>`. The target-url proof script also rejects packaged verifier output that does not report `status: ok`, enough persisted `computerUseEnvironmentCount`, or the configured uniqueness echo/count. If strict mode fails on `not_assessed`, `DEMO_NOT_ASSESSED`, unreadable artifact bytes, duplicate screenshot bytes under a required uniqueness threshold, persisted `nextAction.approvalToken`, or persisted `nextAction.text` for a credential-like type target including OTP/MFA/passcode/PIN-style labels, keep Cluster B open.

Source-repo maintainers may also run the mirror script when validating the Python proof tooling itself:

```bash
python3 scripts/verify_external_computer_use_bundle.py --bundle <external-bundle.json>
```

### D. Prepare generic project-profile onboarding inputs

Use this when a target repository needs a reusable onboarding path and should not depend on this workspace's repo-local self-dogfood helper assumptions.

Read `project-profile-onboarding.md` for the generic project-profile onboarding lane.

From the repository root or installed skill bundle root:

```bash
python3 .agents/skills/uat-demo-agent/scripts/prepare-project-profile-inputs.py \
  --profile temp/project-profile.json
```

Expected result: a `<profile-id>-manifest.json` and `<profile-id>-request.json` pair that can be fed into the existing generic `plan generate` / `plan validate` flow.

### E. Dogfood the skill against this repo

This is a **repo-local maintainer lane**, not the generic packaged-skill success path for arbitrary target repos.

Run this from the repository root when you want the packaged skill surface to plan against this workspace's own specs/manual/review inputs:

```bash
bash .agents/skills/uat-demo-agent/scripts/prepare-self-dogfood-inputs.sh
bash ./scripts/uatdemo.sh plan generate \
  --manifest temp/uat-demo-self-dogfood-manifest.json \
  --request temp/uat-demo-self-dogfood-request.json \
  > temp/uat-demo-self-dogfood-plan.json
bash ./scripts/uatdemo.sh plan validate --file temp/uat-demo-self-dogfood-plan.json
bash .agents/skills/uat-demo-agent/scripts/classify-self-dogfood-plan.sh \
  temp/uat-demo-self-dogfood-plan.json
```

Suggested capture flow:

1. Generate the manifest/request pair into `temp/`.
2. Generate the draft plan and save stdout to `temp/uat-demo-self-dogfood-plan.json`.
3. Validate that draft before deciding whether a follow-on executable `run demo` or `run uat` lane is realistic.
4. Run the classifier helper on the generated plan.

Expected result: a `valid-draft` `plan-definition` payload that exercises the repo's own packaged CLI + skill contracts against this workspace without overclaiming executable readiness.

Do not treat this cookbook as the default cross-project onboarding pattern. For a different repository, keep using the generic manifest/request contracts and `project-profile-onboarding.md` rather than copying the self-dogfood helper assumptions from this workspace.

## Preflight checklist for general agents

Before running anything, check:

1. the chosen binary actually resolves
2. the input file exists
3. the state path is understood and ignored by `.gitignore` if project-local
4. for `report show`, the report file path exists
5. for `report publish`, the bundle, report JSON, and referenced artifacts all exist locally
6. for `run windows-vm-computer-use`, the VM lifecycle prerequisites are available, `--vm-instance` or `UATDEMO_WINDOWS_VM_INSTANCE` points to the intended existing VM when needed, the dedicated VM agent is running inside the logged-in desktop when `--sidecar-attachment-mode dedicated-agent` is used, and the resulting bundle is read back before claiming success

## Decision hints

- If the user asks “先 review 還有什麼會阻擋 UAT/demo, 然後進行 UAT”, first read `.agents/specs/SPECS.md`, `.agents/specs/RTM.md`, and `.agents/specs/NEXT_STEPS.md`, then separate **strategic blockers** from the **local runnable web UAT path**.
- If the user has no plan yet, do not jump straight to `run uat`; prepare or generate a plan first.
- If the user asks for Windows VM computer-use proof and already has a scenario file, prefer `run windows-vm-computer-use --file <scenario.json> --vm-instance <domain-or-instance> --sidecar-attachment-mode dedicated-agent` over hand-authoring raw `windows-vm` plan JSON when a specific VM is known and the session-resident VM agent is active.
- If the output is missing the expected structured fields, do not call it success just because the exit code is zero.

## Source-repo cooperation shortcuts

When the workspace is this source repo:

1. `spec-master` remains the routing authority.
2. `spec-driven-development` remains the branch-spec authoring authority.
3. `spec-registry-manager` remains the `SPECS.md` registry authority.
4. Improvement findings go to `.agents/specs/ISSUE_LOG.md` first, then get assigned to `.agents/specs/ISSUE_LOG.md#cluster-work-packages`, ranked, and owner-resolved before a new spec or CR is opened.
5. `uat-demo-agent` owns these repo-local operator lanes:
   - `bash scripts/refresh_tracked_consumer_docs.sh`
   - `python3 scripts/prove_skip_binary_refresh.py`
   - `python3 scripts/publish_repo_owned_skills.py report --all --compatibility-summary --require-known-proof-sources`
   - `python3 scripts/publish_repo_owned_skills.py publish --skill uat-demo-agent --install-global --skip-binary-refresh`
