---
name: shared-governance
description: 共用治理規則與範本的中立 skill。當工作涉及 repo-owned global skill wording、shared workflow、git branch / worktree isolation、concurrent writable lanes、governance artifact conflict prevention、或需要跨多個治理 skills 重用同一套流程模板時使用。它提供 global-skill 內建 references，避免把這些共用規則依附在單一 skill 或依賴 AGENTS.md 才成立。
---

# Shared Governance

這個 skill 承載 **多個 global skills 共同依賴** 的治理規則與範本。

它的目標不是取代 `spec-master`、`spec-driven-development`、`test-registry-manager`、`spec-registry-manager`，而是提供一個中立的 shared reference layer，讓這些 skills 不必把共用 git/worktree/conflict 規則掛在單一 skill 名下。

## 角色定位

你負責：

- 提供共用的 git branch / worktree governance 規則
- 提供 concurrent writable lanes 的 conflict-prevention 與 downgrade 流程
- 提供共享的 branch namespace、worktree layout、命令片段、handoff checklist
- 提供 pre-write conflict checklist，讓多個治理 skills 可直接引用

你不負責：

- 代替下游 skill 自己完成 spec authoring
- 自己裁決 `review.md` readiness verdict
- 自己維護 `SPECS.md`、`TESTS.md`、`RTM.md` 的 row-level 或 spec-level內容
- 自己分配 local runtime ports / stacks / live infra ownership

## 何時使用

- 使用者在問 shared governance wording、共用 workflow 邏輯、或多個 global skills 共用的治理規則
- 使用者在問 branch/worktree isolation、audit lane、authoritative writable lane、cleanup/prune
- 使用者在問多條 lane 同時碰 `SPECS.md`、`TESTS.md`、`RTM.md` 時如何避免衝突
- 需要一份不依賴 repo-local `AGENTS.md` 的 global template / checklist

## 何時不要使用

- 單純 route spec 工作 → `spec-master`
- 單純做 branch-spec authoring / tasks / implementation / review → `spec-driven-development`
- 單純處理 test registry → `test-registry-manager`
- 單純處理 spec registry → `spec-registry-manager`

## Canonical References

需要共用規則時，依序讀取：

- `./references/git-worktree-guide.md`
- `./references/git-worktree-templates.md`
- `./references/concurrent-writable-lanes.md`
- `./references/pre-write-conflict-checklist.md`
- `./references/ownership-evidence-template.md`
- `./references/conflict-evidence-review-checklist.md`
- `./references/cross-artifact-regeneration-order.md`

需要 deterministic gate 時，使用：

- `./scripts/validate_governance_writeback.py`

## 使用原則

- 共用規則優先存在於 global skills 內建 references
- repo-local `AGENTS.md` 若存在，只能補充或 override，不應成為這些共用流程的唯一來源
- 下游 skill 應引用這裡的 canonical references，而不是把同一套規則複製貼上到各自的 body 中
- ownership evidence、review-time conflict proof、與 cross-artifact regeneration order 也應由這裡集中定義，避免各 skill 各自發明版本
- 若需要在正式 writeback 前做輕量驗證，優先用這個 skill bundled 的 validation script，而不是即興檢查
