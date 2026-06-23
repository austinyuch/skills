# Spec Master Routing Matrix

| User intent / signal | Primary route | Expected authority | Must not do |
| --- | --- | --- | --- |
| 新建 feature spec、寫 requirements / design / tasks / review | `spec-driven-development` | branch-spec artifacts | 不要先改 `SPECS.md` 取代 authoring |
| 繼續既有 spec、下一步、resume、中斷恢復 | `spec-driven-development` | `NEXT_STEPS.md` + active spec state | 不要只靠 `NEXT_STEPS.md` 跳過 `SPECS.md` 檢查 |
| 更新 `SPECS.md`、盤點 specs、同步 registry wording | `spec-registry-manager` | `SPECS.md` registry | 不要把 `NEXT_STEPS.md` 當 registry entry |
| 更新 `TESTS.md`、盤點 test catalog、整理 test traceability / stale rows / duplicate IDs | `test-registry-manager` | folder-level `TESTS.md` + workspace `.agents/specs/TESTS.md` | 不要把 `RTM.md` / `SPECS.md` 當 row-level test authority |
| 完整盤點 / 建立 `RTM.md`，但來源仍是 spec artifacts | 預設走 `spec-driven-development`；只有 workspace 已明確定義既有 RTM-maintaining flow 時才改走該 flow | workspace-level traceability rollup | 不要把 `RTM.md` 當 spec-level authoring truth |
| gap / tech debt / known issues 要納入適合的 spec 追蹤 | `spec-driven-development` 或 `issue-log-manager` | impacted branch-spec / issue log | 不要直接把 issue log 摘要塞進 `SPECS.md` 當唯一追蹤面 |
| FMEA 納入 SDD spec / design / tasks | `spec-driven-development` | active spec artifacts | 不要在 router 內重寫 FMEA methodology |
| manual / review 文件更新，但主問題是 stakeholder artifact generation | downstream specialized skill after spec context is clarified | project review / manual artifacts | 不要讓 router 直接成為 review/manual generator |
| 啟動 / 重用 / 釋放 backend/frontend/UAT/E2E stack | `local-infra-registry-governance` | local infra registry | 不要猜 ports、stack names、instance ownership |
| 使用者已明確指定某個下游 skill | honor explicit skill unless it violates boundaries | user-selected downstream skill | 不要靜默改用別的 skill 而不說明 |
