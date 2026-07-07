# Spec Master Family

`spec-master` is the front door for the Spec Master family: a routing skill that stops governance work from being misfiled as spec work, test work, runtime work, or ad hoc memory.

This README is designed as a packageable explanation and sales brief. It should travel with `skills/spec-master/` when the family is delivered as a bundle.

## One-Line Value Proposition

Spec Master gives coding agents one governed operating model for routing work, writing specs, refreshing registries, managing test evidence, holding unresolved issues, maintaining project-level architecture steering, and allocating local runtime resources without confusing those responsibilities. The value is not abstraction for its own sake; it is reducing misroutes, stale evidence, and ownership drift on real multi-agent repos.

## First Principles

Agentic AI changes software work from linear handoff to delegated coordination. Agents can now produce text, mutate files, call tools, and hand work to other agents faster than humans can manually re-establish context, so the bottleneck shifts from raw output to decision quality and boundary control.

What becomes more valuable:

- choosing the right owner before work starts
- keeping authority surfaces separate from derived summaries
- making evidence fresh enough to trust
- keeping runtime state out of governance text

What becomes more fragile:

- a green file that looks authoritative but is not
- one skill trying to own planning, evidence, and execution at once
- stale summaries being mistaken for readiness
- faster movement that hides deeper coordination debt
- vendor-specific coding-agent behavior becoming the team's unreviewed process by accident

Role lens:

- CEO: value is higher throughput, lower coordination cost, and reusable governance packaging; risk is scaling confusion faster than the organization can absorb it
- CIO: value is clearer ownership and a stable operating model; risk is fragmented authority surfaces and policy drift across tools and repos
- DevSecOps: value is cleaner evidence chains and safer handoff language; risk is false confidence, mixed readiness signals, and security gaps that arrive too late

This is why traditional agile practices need to get stricter, not looser. Smaller stories are not enough if ownership, evidence, and runtime boundaries remain blurry. CI/CD needs stronger gating on freshness and traceability. Code review needs to become more deterministic about evidence, not just more verbose about opinions.

Spec Master answers that by separating routing from authoring, registry sync, test evidence, issue holding, runtime allocation, and shared guardrails into distinct owners with explicit claim boundaries.

There is also a governance reason to own the workflow locally. Coding agents change quickly, each vendor makes different orchestration choices, and many decisions remain partly black-box. A team that relies only on tool behavior cannot reliably explain why work was routed, why evidence was trusted, or why a claim was upgraded. Spec Master gives the team an inspectable workflow, evidence trail, and retrospective surface so process improvements belong to the team rather than to a vendor's hidden defaults.

## Scrum Team Mapping

| Scrum 角色 | Spec Master 的對應責任 | 產生的價值 / 風險控制 |
| --- | --- | --- |
| Product Owner | 把需求先路由到正確的治理面，再決定要不要進入分支規格或暫存區 | 讓 Backlog 先有責任歸屬，避免把模糊需求直接寫成假規格 |
| Scrum Master | 維持路由規則、跨技能協作與澄清節奏 | 降低重複澄清、交棒混亂與權責漂移 |
| Developers | 使用正確的下游技能執行規格、註冊、測試與執行環境工作 | 減少上下文切換，讓實作與治理不互相污染 |

Spec Master 強化的是 Scrum Team 的邊界管理：先分清誰負責什麼，再開始實作。它不是取代 Scrum，而是讓 Scrum 在代理人協作下仍然能守住責任分工。

## Agile Manifesto Mapping

| Agile 價值 | Spec Master 如何支撐 | 如果沒做到會壞掉什麼 |
| --- | --- | --- |
| Individuals and interactions over processes and tools | 透過明確路由與權責面，讓人與代理人更快知道該找誰 | 工具越多，協調越慢，大家都在猜 owner |
| Working software over comprehensive documentation | 讓文件只做權責與證據，不假裝成完成宣稱 | 文件變成權威假象，工作軟體反而被延遲 |
| Customer collaboration over contract negotiation | 先把需求送到正確 owner，再把可交付內容對齊 | 客戶問題被治理文字稀釋，無法快速回應 |
| Responding to change over following a plan | 允許在 owner 不明、證據過舊、runtime 未定時快速重路由 | 變更被舊計畫綁住，風險會在晚期才爆出來 |

這些對應不是抽象口號。它們直接告訴團隊：在 Agentic AI 時代，敏捷不是放鬆控制，而是更早鎖定責任、更早驗證證據、更早隔離執行環境狀態。

## Three Demand Dimensions

| Dimension | What it means here | Executive value |
| --- | --- | --- |
| 獲益 | Less rework, faster handoff, reusable governance packaging | CEO 觀點(Chief Executive Officer)：降低協調成本、加快交付 |
| 任務 | Route governance work to the right owner before editing any artifact | CIO 觀點(Chief Information Officer)：更清楚的單一事實來源邊界與責任歸屬 |
| 痛點 | Misroutes, stale evidence, and runtime state leaking into docs | DevSecOps 觀點：更安全的交棒語言、更新鮮的證據、更少錯誤宣稱 |

CEO 觀點(Chief Executive Officer)：這會降低工作啟動成本，並減少團隊為同一個澄清重複付費的次數。

CIO 觀點(Chief Information Officer)：這會透過分離單一事實來源面、衍生摘要與執行環境狀態來保護權責模型。

DevSecOps 觀點：這會把執行環境邊界、證據新鮮度與就緒語言分開，避免營運者承接錯誤自信。

## Responsible AI 需求與解法

Responsible AI 在本家族中不是另開一套抽象倫理口號，而是把可信任人工智慧(Trustworthy AI) 要求落到 routing、authority boundary 與 evidence handoff。可對齊的外部要求包括：NIST AI Risk Management Framework 的風險管理與 trustworthiness 設計目標、OECD AI Principles 的人權公平、透明、安全與問責原則，以及 ISO/IEC 42001 對 AI 管理系統、責任使用、透明度、風險與機會治理的要求。

| Responsible AI 需求 | Spec Master 解法 | 為什麼有商業價值 |
|---|---|---|
| Human agency / oversight 人類監督 | `spec-master` 先做 owner routing，不讓 agent 直接把模糊請求寫進下游 artifact；需要人類確認時保留 handoff 與 blocker。 | 避免黑盒代理人替團隊做不可追溯決策，降低錯誤承諾與責任不清。 |
| Accountability 問責 | 每個治理 surface 都有明確 owner：spec authoring、registry、tests、issue log、runtime、shared guardrails 分屬不同 skill。 | 讓管理者知道該找誰修正，不把所有問題都丟回「agent 做的」。 |
| Transparency / explainability 透明與可解釋 | 路由理由必須基於 authority surface，而不是檔名直覺；下游 handoff 說清楚為什麼交給某 skill。 | 降低 adoption 阻力，讓團隊能審查與改進自己的工作流。 |
| Robustness / safety 穩健與安全 | 避免 runtime state、stale summaries、test rollups、readiness verdict 混在同一文件；遇到 drift 先重路由。 | 防止錯誤權威面導致部署、demo 或 audit 期間出現錯誤信心。 |
| Privacy / data governance 隱私與資料治理 | routing 階段不把 secrets、runtime allocation、或敏感執行環境細節寫進 `SPECS.md` / `NEXT_STEPS.md`。 | 降低機敏資料擴散到可打包文件或跨團隊摘要的風險。 |
| Fairness / bias management 公平與偏誤管理 | 對需求、issue、review finding 先做 owner resolution 與 evidence classification，避免單一 agent 的偏好直接變成正式 spec。 | 讓優先順序由證據與產品責任決定，而不是由某次模型輸出決定。 |
| Auditability / continual improvement 可稽核與持續改善 | `ISSUE_LOG.md`、`NEXT_STEPS.md`、`SPECS.md` 與 downstream review artifacts 形成可回顧的決策鏈。 | 支撐 retrospective、流程改善、內部稽核與跨 vendor 更換。 |

換句話說，Spec Master 家族把 Responsible AI 的高階要求轉成三個可執行控制：先分清 owner、再限制 claim、最後保留 evidence trail。

參考來源：

- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [OECD AI Principles](https://oecd.ai/en/ai-principles)
- [ISO/IEC 42001:2023 AI management systems](https://www.iso.org/standard/42001)

## What You Lose If You Merge These

- If `spec-master` and `spec-driven-development` are merged, the router starts acting like the spec author, and intake cost rises because every ambiguous request now drags a full workflow with it.
- If `spec-registry-manager` and `test-registry-manager` are merged, registry wording and test evidence start sharing one authority model, which makes stale evidence harder to spot.
- If `issue-log-manager` and `local-infra-registry-governance` are merged, unresolved work and runtime allocation get mixed together, which hides whether a problem is a planning gap or an operations gap.
- If `system-architect` is merged into `spec-driven-development` or `project-review-skill`, project-level architecture steering starts competing with branch-spec `design.md` or executive narrative, and stale diagrams can become accidental readiness claims.

The practical loss is not abstract: merged skills create more reroutes, more false confidence, and more backtracking when a repo grows beyond one owner’s head.

## Why This Family Exists

Large projects usually fail at coordination before they fail at syntax. Common failure modes include:

- Different agents route the same request to different workflows, so the team pays repeated clarification cost.
- `SPECS.md`, `NEXT_STEPS.md`, `RTM.md`, `TESTS.md`, and `review.md` start competing as truth, which makes handoffs fragile.
- Test summaries stay green while the underlying evidence is stale, so confidence rises faster than signal.
- Follow-up issues become informal memory instead of governed work, which means the same gap gets rediscovered.
- Runtime ports, local stacks, and demo state leak into spec or registry files, creating false authority.
- Stakeholder-facing manuals, reviews, and architecture steering overstate what the evidence proves, which hurts adoption and reuse.

The Spec Master family separates those responsibilities and reconnects them through explicit handoffs. Each subskill exists because one kind of drift needs one kind of owner, not because we wanted a larger menu.

## Family Members

| Skill | Role | Primary Authority | Why it stays separate |
| --- | --- | --- | --- |
| `spec-master` | Front-door router and improvement classifier | Routing decision only | Keeps intake simple so ownership is decided before work starts |
| `spec-driven-development` | Requirements, design, tasks, implementation, review, optimization | Branch-spec artifacts | Needs a full spec lifecycle, not a router shortcut |
| `spec-registry-manager` | Stable `SPECS.md` lifecycle and CR summary reconciliation | Spec-local artifacts and CR files | Registry sync has different authority from branch-spec authoring |
| `test-registry-manager` | `TESTS.md` catalog, traceability, freshness, and rollup governance | Folder-level `TESTS.md` first | Test evidence ages differently from spec text and must be maintained separately |
| `issue-log-manager` | Holding surface for unresolved improvements without safe ownership yet | `.agents/specs/ISSUE_LOG.md` | Prevents half-owned gaps from becoming accidental specs |
| `local-infra-registry-governance` | Local dev / UAT / E2E runtime allocation, reuse, release, and reconciliation | Local infra registry | Runtime state changes live outside spec governance |
| `system-architect` | Cross-spec project architecture steering inspired by Kiro foundational steering, `.agents/steering/{product,tech,structure}` markdown/HTML, and code-review context packets | Accepted specs, reviews, code evidence, and steering docs | Architecture communication spans specs and should not be hidden inside one branch `design.md` or stakeholder review |
| `shared-governance` | Reusable git/worktree, ownership, and derived-artifact guardrails | Shared governance references | Shared guardrails must apply across families, not sit inside one workflow |

## Operating Model

Use `spec-master` first when a request touches spec or governance surfaces and the correct owner is not obvious. The job is to save a human or agent from guessing the owner, not to perform the downstream work itself.

Typical routing:

- New feature, complex fix, design, tasks, implementation, review, or optimization -> `spec-driven-development`
- `SPECS.md` lifecycle summary, CR summary, or registry wording -> `spec-registry-manager`
- `TESTS.md` rows, stale evidence, duplicate IDs, test traceability -> `test-registry-manager`
- Known issue, retro finding, tech debt, or repeated gap without a safe owner -> `issue-log-manager`
- Local backend/frontend/database/UAT/E2E allocation or reuse -> `local-infra-registry-governance`
- Project-level architecture steering, `.agents/steering/{product,tech,structure}` markdown/HTML, stale architecture review, or code-review Architecture Context Packet -> `system-architect`
- Cross-lane git/worktree ownership and writeback safety -> `shared-governance`

Why this split helps: teams stop paying the cost of one agent rewriting another agent's authority surface. A routing skill is cheaper to maintain than a monolithic workflow, and it makes the downstream contract more legible when the same repo has specs, tests, runtime state, architecture steering, and review evidence in play.

The rule is simple: route by authority surface, not by whichever file was mentioned first.

## When To Use

Use `spec-master` when:

- a request touches specs, registries, tests, issue holding, architecture steering, runtime allocation, or shared governance and the owner is unclear
- the task is routing work to the right downstream skill before any file is edited
- the repo needs a stable front door for governance work across multiple agents

Do not use `spec-master` when:

- the owner is already obvious and the task belongs directly to a downstream skill
- the work is purely writing content without a routing decision
- you are trying to produce a readiness verdict instead of a routing decision

The practical test is simple: if the main decision is "who should own this?", use `spec-master`. If the main decision is "how do I do the work?", go to the owner directly.

## Outcome Signals

The family is doing useful work when you see:

- fewer clarification loops before a task is owned
- cleaner handoffs because evidence and routing are separated
- fewer stale summaries or runtime claims leaking into governance docs

## Amazon Backwards Press Release

**SpecMaster 團隊推出 Spec Master Family to keep coding agents aligned on one engineering truth model**

Taipei, June 18, 2026 - SpecMaster 團隊 today introduced the Spec Master family, a governance skill bundle that helps engineering teams and coding agents move from ambiguous requests to traceable delivery without losing ownership, evidence, or runtime boundaries along the way.

For teams using multiple coding agents, the hardest problem is often not generating code. It is keeping every agent aligned on what kind of work is being done, which artifact is authoritative, and when a claim is backed by real evidence. Spec Master solves this by giving agents a front door for routing and a family of downstream skills for the work that follows.

"We wanted the agent to stop guessing whether a request was spec authoring, registry sync, test governance, runtime setup, or an unresolved improvement," said the SpecMaster 團隊. "Spec Master makes that decision explicit before files are edited."

The family combines spec-driven delivery, stable registry reconciliation, test catalog governance, unresolved issue holding, runtime allocation boundaries, and shared worktree guardrails. The result is a workflow that favors working software and honest evidence over polished but unverified summaries.

Spec Master is available as a packageable global skill family rooted at `skills/spec-master/`. `spec-master` is the single package root and front door; the downstream skills — including `spec-driven-development` for branch-spec delivery and `system-architect` for project-level architecture steering — are individual sibling skills expected to be installed alongside it under the same `skills/` home. There is no separate dependency manifest; each sibling is its own installable skill folder.

## FAQ

### Who is this for?

Teams using coding agents on non-trivial repositories, especially when work spans specs, tests, runtime environments, stakeholder documents, and follow-up governance.

### Why not just use one large workflow skill?

Because one workflow quickly becomes a blurred authority surface. In practice that means a spec skill starts making registry promises, a registry skill starts looking like a test authority, and runtime state gets smuggled into documentation. Spec Master keeps routing separate from authoring, registry sync, test governance, issue holding, and runtime allocation so each contract stays inspectable.

### Does `spec-master` write specs?

No. `spec-master` classifies the request and hands branch-spec authoring to `spec-driven-development`.

### Why is `issue-log-manager` separate?

Because unresolved work is a different economic problem from approved spec work. If you turn a vague gap directly into a spec, you lose the record of why it was unclear and you encourage the same issue to be rediscovered later.

### Why is `local-infra-registry-governance` separate?

Because runtime allocation is an operational resource problem, not a documentation problem. Keeping it separate prevents ports, stacks, and demo environments from masquerading as spec truth.

### Why is `system-architect` separate?

Because project-level architecture steering cuts across multiple specs. Inspired by Kiro's foundational steering split, it reconciles accepted `design.md`, `review.md`, code evidence, and code-review context into `.agents/steering/product.md`, `tech.md`, and `structure.md` plus same-name HTML without turning those steering files into branch-spec authority or readiness verdicts.

### Does this replace human review?

No. It improves traceability and handoff discipline. Final readiness and acceptance still belong to review artifacts such as `review.md` and to the team’s governance process.

### How does it prevent false confidence?

It caps claims by evidence source, keeps `review.md` as readiness authority, prevents derived-to-derived refresh loops, and routes stale test evidence to `test-registry-manager`.

### How should this be packaged?

Package `skills/spec-master/` as the front-door artifact and include the core family skills listed above, including `system-architect`. This README and `GENERATION_GUIDE.md` are the customer-facing explanation and maintenance contract.

## Evidence And Claim Boundary

This README explains the governance product. It does not claim that a consuming repository is demo-ready, production-ready, or fully integrated. Those claims must come from the consuming repo's own `review.md`, test evidence, runtime registry state, and related authority surfaces.

## Maintenance

When the family routing model, downstream skill list, authority boundaries, or packaging expectations change, update this README using `GENERATION_GUIDE.md`.
