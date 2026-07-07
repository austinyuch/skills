---
name: agentic-scrum-governance
description: 當使用者要設計、評估、修正或推廣 Agentic Scrum / agent swarm self-upgrade / review trigger / retrospective trigger / global-skill governance 時使用。也用在 agentic Scrum 需要納入跨 spec system architecture drift、architecture review signal、或架構 ownership / handoff 問題時讀取這個 repo 內的正式治理 references，而不是依賴零散 side docs 的情況。
---

# Agentic Scrum Governance

這個 skill 提供 Agentic Scrum / agent swarm self-upgrade 的治理參考資料入口。

## 使用時機

- 使用者詢問 agentic Scrum 應如何運作
- 使用者要定義 review trigger / retrospective trigger
- 使用者要規劃 global skill governance
- 使用者要判斷某個流程問題應留在 spec-local、升級為 shared process，或成為 skill change candidate
- 使用者要判斷跨 spec 架構漂移、架構 ownership、或架構 handoff 問題是否應成為 Sprint Review / Retro / skill 改善輸入

## 讀取順序

1. 先讀 `references/scrum-sdd-double-loop-plan.md`
2. 若要規劃具體變更，再讀 `references/scrum-sdd-double-loop-change-operation-template.md`

## 邊界

- 本 skill 提供的是 reusable governance references，不是最終 readiness verdict surface。
- 若工作涉及正式 global skill 變更，仍應回到 `spec-master` / `spec-driven-development` 的 spec workflow。
- 若工作需要建立、刷新或審查 project-level architecture markdown/HTML，交由 `system-architect`；本 skill 只定義 Scrum / double-loop 何時把 architecture drift 當成 review/retro 訊號。
