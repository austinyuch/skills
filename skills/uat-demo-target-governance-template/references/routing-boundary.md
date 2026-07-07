# Routing Boundary

這份 reference 定義 reusable governance template 與既有 global skills 的 authority split。

這裡描述的是 global skill layer 的 reusable routing logic，應維持在 machine-scoped global skill roots，例如：

1. `~/.codex/skills/`
2. `~/.config/opencode/skills/`

target repo 不應複製整份 cross-skill routing matrix；target repo 只需提供 relevant global skills 會讀取的 repo-local artifacts。

## Primary split

- `spec-master` 是 routing / triage authority。
- `spec-driven-development` 是 phase-authoring authority。
- `uat-demo-agent` 是 execution / evidence authority。

## Routing matrix

1. 當使用者在判斷 active spec、truth surface、下一步應導向哪個 skill 時，先用 `spec-master`。
2. 當使用者已經進入 requirements/design/tasks/implementation/review 任一 spec phase 時，交給 `spec-driven-development`。
3. 當工作是 `plan generate`、`plan validate`、`run uat`、`run demo`、`report show` 時，交給 `uat-demo-agent`。
4. 當工作是 `SPECS.md`/registry summary 同步時，交給 `spec-registry-manager`。
5. 當工作是 browser validation 時，交給 `webapp-testing`。
6. 當工作是 manual/demo-support artifact 生成時，交給 `user-manual-skill`。
7. 當工作是 final verification 時，交給 `verification-loop`。

## Non-goals

1. 不要讓 `spec-master` 重新講一套 spec phase authoring 規則。
2. 不要讓 `spec-driven-development` 變成 routing catalog。
3. 不要讓 companion template skill 取代上述 authority skills。
4. 不要把這份 reusable routing matrix 原封不動搬進 target repo。
