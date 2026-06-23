# UAT To Demo Transition

這份 reference 定義從 UAT iteration 切到 demo preparation 的 reusable gate。

## Stay in UAT iteration when

1. 還有 blocker triage 未完成
2. 還有 target-owned runtime gap
3. evidence posture 仍是 `not_assessed` 或需要 follow-on spec / CR
4. `uat-demo-agent` 只產出 execution/evidence surfaces，尚未完成後續修正與驗證

## Move to demo preparation when

1. 主要 blocker 已被明確關閉或降級
2. 需要的 target runtime path 已完成 governed verification
3. 需要的 UAT iteration follow-ons 已完成或有明確 bounded handoff
4. operator 可以明確轉交 `user-manual-skill`、`webapp-testing`、或 demo-oriented follow-on spec

## Handoff

1. 若需要開新 spec 或續做 spec phase，回到 `spec-driven-development`
2. 若只是判斷下一步屬於哪個 authority，先走 `spec-master`
3. 若要跑 execution / evidence，回到 `uat-demo-agent`
