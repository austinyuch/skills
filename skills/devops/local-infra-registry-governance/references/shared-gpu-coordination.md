# Shared GPU Coordination (host `gx10-fb46`, single GB10)

> **Why this exists.** This machine has **one** GB10 GPU with **~121 GB unified CPU+GPU memory**.
> Several projects run heavyweight model workloads on it. The `local-infra-registry` schema has **no
> GPU/device primitive and no cross-project mutex primitive**, so GPU contention is governed by the
> **convention** documented here, not by a `registry.json` entry. Two heavyweight GPU jobs running at
> once will **OOM** the shared unified memory and kill each other. Read this before launching any
> container/process that consumes the GPU.

This reference is the machine-scoped, cross-project source of truth. The contending consumers each live
in their own repo; the canonical policy table is duplicated (intentionally, as stable policy) in
`aclab-middlewares/AGENTS.md` → section **"Shared GB10 GPU — single-tenant mutex convention"**.

## The device

| Fact | Value |
|---|---|
| Host | `gx10-fb46` (DGX Spark GB10) |
| Arch | aarch64 (Grace-Blackwell) |
| Memory | **~121 GB unified** — CPU and GPU share one pool; there is no separate VRAM budget |
| GPU-in-container | CDI `nvidia.com/gpu=all` (works for both Docker and Podman) |
| Inspect occupancy | `nvidia-smi` (process list); `docker ps` / `podman ps` for GPU containers |

> GB10 reports `Memory-Usage: Not Supported` in `nvidia-smi` (unified memory). Use **`free -g`** as the
> real free-memory signal, plus the process list, to judge whether the card is busy.

## Known GPU consumers and their owners

Each consumer is governed by its **own** lifecycle owner. Live occupancy is read from that owner +
`docker ps`, **never** from `registry.json`.

| Consumer | Owns / lives in | Lifecycle authority | Check / release |
|---|---|---|---|
| **vLLM `local-nemotron`** (Nemotron-120B NVFP4), Docker `172.17.0.1:18000` | `aclab-middlewares` repo | `vllm-serving-manager` skill → `vsm` (registry `vllm-serving/model-registry/`) | `vsm status` / `vsm stop` |
| **DoMINO / PhysicsNeMo GPU jobs** (e.g. H2 B0 probe, H3/H4 training) | `giant-aero` / `giant-aero_spec13` | the giant-aero spec itself (`aero-surrogate-strategy/HANDOFF.md` §H2). **Not** an aclab-middlewares service — do not model it as local infra | `docker ps` for the nvcr/PhysicsNeMo container; stop the container |
| Ad-hoc JAX/CFD training (giant-aero) | `giant-aero` | `scripts/resource_orchestrator.py` (its own GPU/CFD memory governor) | that orchestrator's status |

vLLM-120B alone can hold the majority of the 121 GB pool; a DoMINO inference+LoRA job needs the GPU too.
They **cannot** coexist.

## The rule

**Never run two heavyweight GPU workloads on the GB10 at the same time.** Concretely, never run vLLM
`local-nemotron` and a DoMINO/PhysicsNeMo GPU job concurrently.

## Preflight before launching a GPU workload

Run this check from any project before starting a GPU container/process:

1. **Is vLLM up?** `vsm status` (in `aclab-middlewares`). If it reports a running `local-nemotron`,
   either wait or `vsm stop` it (only with the operator's agreement — it is another project's service).
2. **Any rival GPU container?** `docker ps` / `podman ps` — look for `vllm`, `nvcr.io/...physicsnemo`,
   or other CUDA images. `nvidia-smi` process list confirms.
3. **Enough free memory?** `free -g` — a 120B-class or DoMINO job wants tens of GB free. If the pool is
   already largely used, do **not** launch.
4. Only when the card is clear: launch your workload, and **stop it when done** so the next project can
   use the GPU. Record external-experiment evidence through your own repo's recorder (for giant-aero B0:
   `scripts/build_b0_results_sidecar.py`), not by faking it.

## Cross-project handshake (how giant-aero finds aclab-middlewares)

When a giant-aero agent needs the GB10 for DoMINO/PhysicsNeMo:

- The vLLM occupant is owned by **aclab-middlewares** at `~/aclab-middlewares`. Its authority is
  the `vsm` CLI (the `vllm-serving-manager` skill), and its stable policy is in
  `aclab-middlewares/AGENTS.md`.
- giant-aero must **not** start its GPU job while vLLM holds the card. Coordinate by checking `vsm status`
  and releasing/waiting, per the preflight above.
- aclab-middlewares, symmetrically, should not `vsm serve` a large model while a giant-aero GPU job is
  running. Same preflight, mirror image.

## What NOT to do

- Do **not** invent a `gpu_exclusive` resource or any GPU entry in `registry.json` — there is no governed
  tool or schema primitive for a physical device or a cross-project mutex. Hand-editing it is a guessed
  allocation and is forbidden by the registry invariants.
- Do **not** treat `scripts/local_infra.py` as the GPU authority — it governs only the
  `dev-shared-services` + `observability` compose bundles and has no GPU notion.
- Do **not** model giant-aero's external GPU experiment as aclab-middlewares local infra, and do not claim
  a GPU run happened locally when it was gated/external.
