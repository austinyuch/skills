# Code Review Family

`code-review` is the front door for a review-oriented skill family that helps agents inspect code structure, produce bounded-context handoffs, and apply deterministic review tooling without confusing that work with runtime readiness. The family exists because most review failures are coordination failures: the wrong concern gets the wrong owner, and the evidence arrives too late to be useful.

This README is the packageable explanation for the family. It should travel with `skills/code-review/` when the skill is installed or redistributed.

## One-Line Value Proposition

Code Review gives coding agents a governed way to analyze code, rank impact, surface maintainability and security issues, and hand off the right next action without pretending static analysis is the same thing as release readiness. The business value is shorter review cycles, fewer duplicated comments, and less time spent reconciling inconsistent tool outputs.

## First Principles

Agentic AI changes code delivery from a mostly human review loop to a mixed human-agent review loop. More code now arrives through model-assisted generation, tool-driven edits, and agent-to-agent handoffs, which means defects can spread faster unless review becomes more structured.

What becomes more valuable:

- separating diagnosis from remediation
- turning review evidence into something reusable by the next owner
- keeping security, tests, and refactor risk visible at the same time
- making readiness language stay outside the review bundle

What becomes more fragile:

- a reviewer who becomes a bottleneck for every concern
- a static-analysis tool being mistaken for a release gate
- refactor advice arriving before defect analysis is clear
- security and test signals collapsing into a single vague comment stream
- vendor-specific coding-agent review behavior becoming the team's unreviewed quality process by accident

Role lens:

- CEO: value is faster delivery with less duplicate review effort; risk is shipping more quickly while hiding latent quality debt
- CIO: value is a standard review contract that can be reused across teams and repos; risk is fragmented authority if review and readiness are not separated
- DevSecOps: value is a stronger evidence chain that keeps security and test signals intact; risk is false green review output that outruns actual readiness

Traditional agile practice has to tighten because agentic work increases the cost of ambiguity. CI/CD needs stronger evidence gates, not just faster builds. Code review needs more deterministic routing of evidence, not just more human comments. The point is to make the review path precise enough that one wrong signal does not get promoted into a release belief.

Code Review answers that by separating review orchestration from test diagnosis, refactor advice, test design, and security preflight, then keeping graph and summary tooling in the role of inputs rather than verdicts.

There is also a governance reason to own the review workflow locally. Coding agents change quickly, each vendor makes different orchestration choices, and many review decisions remain partly black-box. A team that relies only on tool behavior cannot reliably explain why a finding was ranked, why a test signal was trusted, or why a static-analysis result became action. Code Review gives the team an inspectable review contract, evidence trail, and retrospective surface so improvement belongs to the engineering team rather than to a vendor's hidden defaults.

## Scrum Team Mapping

| Scrum 角色 | Code Review 的對應責任 | 產生的價值 / 風險控制 |
| --- | --- | --- |
| Product Owner | 取得可行的審查證據，判斷哪些風險需要先進 Backlog | 讓優先順序建立在證據上，而不是印象上 |
| Scrum Master | 維持審查節奏、阻塞回報與跨角色協調 | 降低 review 卡關、重工與責任不清 |
| Developers | 消化審查結果、修補缺陷、拆分測試與重構工作 | 讓回饋直接變成行動，而不是只留在 comment |

Code Review 強化的是 Scrum Team 的回饋迴路：審查不是最後一道評論，而是讓下一個 Sprint 更準確的決策輸入。

## Agile Manifesto Mapping

| Agile 價值 | Code Review 如何支撐 | 如果沒做到會壞掉什麼 |
| --- | --- | --- |
| Individuals and interactions over processes and tools | 讓每個審查意見都能交給下一位工程師直接採取行動 | Comment 變成訊息垃圾，沒有人真的被幫到 |
| Working software over comprehensive documentation | 以可驗證的缺陷、測試與安全證據支撐判定，而不是堆滿文字 | 文字很多，真正可交付的軟體品質卻不明 |
| Customer collaboration over contract negotiation | 把風險與取捨轉成可討論的審查輸出，方便和產品方對齊 | 需求與品質被切成兩套語言，決策成本上升 |
| Responding to change over following a plan | 當新證據出現時快速重排風險、重構與測試建議 | 舊判斷拖住新變更，修正會晚到變貴 |

這些對應說明的是：Agentic AI 下的敏捷，不是流程更少，而是回饋更快、更準、更能被下一位人或代理人接住。

## Three Demand Dimensions

| Dimension | What it means here | Executive value |
| --- | --- | --- |
| 獲益 | Faster review cycles, fewer duplicate comments, more predictable handoff | CEO 觀點(Chief Executive Officer)：更少審查阻力、更多吞吐量 |
| 任務 | Analyze code, test quality, refactor risk, and security in one governed review path | CIO 觀點(Chief Information Officer)：不同團隊都能重用的單一審查契約 |
| 痛點 | Fragmented tools, partial evidence, and blurred readiness language | DevSecOps 觀點：更強的證據鏈與更安全的交棒語言 |

CEO 觀點(Chief Executive Officer)：這會縮短程式變更到可行審查回饋之間的週期。

CIO 觀點(Chief Information Officer)：這會標準化審查證據，讓不同團隊與不同專案都能使用同一份審查契約。

DevSecOps 觀點：這會把測試品質、重構建議、安全預檢與掃描器接入維持在同一條證據鏈中，同時不模糊就緒宣稱。

## Responsible AI 需求與解法

Responsible AI 在 Code Review 家族中的重點，是讓代理人產生或修改的程式碼不因速度變快而逃過透明、問責、安全、偏誤與可稽核要求。Code Review 不把自己宣稱成 release gate；它把 NIST AI RMF、OECD AI Principles 與 ISO/IEC 42001 常見的 trustworthy / responsible AI 要求轉成可重複的 review evidence 與 handoff contract。

| Responsible AI 需求 | Code Review 解法 | 為什麼有商業價值 |
|---|---|---|
| Human oversight 人類監督 | Review output 是 required input，不是自動合併決策；最終 acceptance / readiness 仍由 consuming repo 的 `review.md` 與人類治理流程裁決。 | 保留人類對 consequential code changes 的決策權，避免工具輸出變成自動放行。 |
| Transparency / explainability 透明與可解釋 | findings 必須指出檔案、行為、風險、證據來源與下一步；graph / summary 只能作為 input。 | 下一位工程師可以理解為什麼要修，不必重新猜測工具判斷。 |
| Accountability 問責 | `code-review`、`test-quality-reviewer`、`security-risk-reviewer`、`code-refactoring-advisor` 各自保留清楚責任邊界。 | 缺陷、測試、重構與安全不再混成模糊評論，owner 更容易接手。 |
| Robustness / safety 穩健與安全 | 用 deterministic review、test-quality、security preflight、Sonar ingest 與 refactor safety-net 捕捉 agent-generated code 的缺陷與安全風險。 | 降低快速變更把 regression、trust-boundary bug 或 insecure output 推進主線的機率。 |
| Privacy / data governance 隱私與資料治理 | review 不應輸出 secrets、PII 或 credentials；local state 與 graph artifacts 應遵守 repo-local state / version-control 邊界。 | 避免審查報告與打包文件成為敏感資訊擴散面。 |
| Fairness / bias management 公平與偏誤管理 | 對 auth、RBAC、tenant boundary、input validation、data access、ranking / filtering logic 保留 security 與 test-design 檢查入口。 | 降低偏誤、越權、資料不當暴露或規則錯配造成的使用者傷害。 |
| Auditability / continual improvement 可稽核與持續改善 | review findings 可轉成 SDD tasks、test obligations、refactor work 或 issue log；輸出保持可重跑與可追蹤。 | 讓 review 不只是一次性評論，而是可衡量、可改善的品質系統。 |

因此 Code Review 家族的 Responsible AI 解法不是「相信工具」，而是把工具輸出限制在 evidence、diagnosis 與 handoff，並把 verdict 保留給 consuming repo 的正式治理面。

參考來源：

- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [OECD AI Principles](https://oecd.ai/en/ai-principles)
- [ISO/IEC 42001:2023 AI management systems](https://www.iso.org/standard/42001)

## What You Lose If You Merge These

- If `test-quality-reviewer` and `test-design-generator` are merged, diagnosis and design get conflated, and the result is either vague recommendations or test ideas that never address the real coverage gap.
- If `code-refactoring-advisor` is merged into `code-review`, the review conversation starts carrying refactor prescriptions before the underlying defect analysis is clear.
- If `security-risk-reviewer` is merged with the main review orchestrator, security triage loses its own vocabulary and the output gets less reusable for the next owner.

The practical loss is slower review cycles, fuzzier ownership, and handoffs that carry more context but less decision quality.

## Why This Family Exists

Large codebases fail in predictable ways:

- Reviews get split across ad hoc tools with different assumptions, so engineers re-explain the same code path several times.
- Impact and dependency reasoning becomes inconsistent across agents, which makes comments hard to trust.
- Test smells and design gaps get missed until late, when the fix is already expensive.
- Security triage and maintainability feedback drift apart, so the next owner gets an incoherent handoff.
- Graph or summary artifacts are treated like verdicts instead of inputs, which produces false confidence.

This family keeps those responsibilities separate. That separation is deliberate: diagnosis, redesign, security preflight, and enriched handoff are different jobs and should not be forced into one opaque review pass.

## Family Members

| Skill | Role | Primary Output | Why it stays separate |
| --- | --- | --- | --- |
| `code-review` | Main review orchestrator | Analysis, reports, bounded-context handoffs | Keeps the first pass focused on review routing and evidence shape |
| `test-quality-reviewer` | Judge existing tests | Smells, FIRST / pyramid gaps, boundary issues | Diagnosis of existing coverage is different from designing new tests |
| `code-refactoring-advisor` | Name code smells and likely refactor moves | Fowler move + test safety net | Refactor naming is advisory work; it should not hide the underlying defect analysis |
| `test-design-generator` | Turn review intent into test cases | Boundary / equivalence / pairwise candidates | Test design is generative, not evaluative |
| `security-risk-reviewer` | Offline OWASP-oriented preflight | Ranked security findings | Security review needs its own lens and vocabulary |
| `sonarqube-bridge` | Ingest Sonar output into the same schema | Sonar + graph-ranked findings | Sonar is an input source, not the authority itself |

## Ponytail / YAGNI Minimality Boundary

The Ponytail Ladder belongs to the code-review family as a pre-review rubric for avoiding
over-building. It supports Phase 2 option selection and Phase 4 implementation/refactoring;
it does not directly participate as a Phase 5 verdict source.

Use it before recommending a new abstraction, helper, dependency, wrapper, parser, lifecycle
manager, class/module split, or test harness:

1. Does this need to exist? If no, skip it.
2. Can the standard library do it? Use it.
3. Can a native platform feature do it portably? Use it, or isolate OS/arch-specific code behind a small adapter with fallback.
4. Can an already-installed dependency do it? Use it.
5. Is it one line? Keep it one line.
6. Only then build the minimum custom implementation.

`code-refactoring-advisor` carries this as `minimality_check` on each refactor finding. The
field is advisory context, not a release gate. It must stay architecture/platform agnostic:
native platform recommendations need portable behavior across the published skill targets, or
an explicit adapter, guard, and fallback for OS/arch-specific behavior.

Do not translate `minimality_check` into `PASS`, `FAIL`, `BLOCK`, or approval language. If the
same change exposes a real compile, portability, runtime, or security regression, route that
verdict to the build/test gates, `review-cli review`, `security-risk-reviewer`, SonarQube, or
the consuming repo's formal review artifact.

## Supporting Tooling

These are orchestrated by the family but are not the core review members:

- `capability-mapper`
- `code-summarizer`

Use them when you need capability graphs or file summaries as inputs to review or handoff work.

## Operating Model

Use `code-review` first when the task is about structure, impact, bounded context, or review assistance. It is the review intake layer, not a generic code explainer.

Typical routing:

- Analyze a file or project -> `code-review`
- Judge existing tests -> `test-quality-reviewer`
- Suggest refactor moves with a safety net -> `code-refactoring-advisor`
- Generate better test cases -> `test-design-generator`
- Run offline security preflight -> `security-risk-reviewer`
- Bring Sonar findings into the same ranking model -> `sonarqube-bridge`

Why this split helps: the same repository often needs diagnosis, redesign, and security triage at the same time. If one skill tries to do all three, the output gets vague and un-actionable. Separate skills let each comment answer one concrete question and give the next owner a cleaner handoff.

The rule is simple: use deterministic review tooling for evidence, and keep acceptance / readiness judgments in the consuming repo's own review artifacts.

## When To Use

Use `code-review` when:

- you need a review front door for a file, directory, or project
- the task is to inspect structure, impact, or bounded context before handoff
- the repo needs one review contract that can absorb test, refactor, security, and scanner evidence

Do not use `code-review` when:

- the task is only to write code without review analysis
- the main work is test design, refactor planning, or security triage already owned by a sibling helper
- you are trying to issue a runtime readiness verdict

If the question is "what is the evidence and what should the next reviewer do?", use `code-review`. If the question is already specific and narrow, go directly to the helper that owns that narrow job.

## Outcome Signals

The family is doing useful work when you see:

- fewer repeated comments on the same code path
- cleaner handoffs because test, refactor, and security evidence stay distinct
- fewer false claims because readiness language remains outside the review bundle

## Amazon Backwards Press Release

**CodeReview 團隊推出 Code Review Family to give coding agents a consistent review and handoff model**

Taipei, June 18, 2026 - CodeReview 團隊 today introduced the Code Review family, a review skill bundle that helps engineering teams and coding agents inspect code, surface maintainability and security issues, and produce bounded-context handoffs without mixing static analysis with readiness claims.

For teams using multiple agents, review quality often breaks down not because the code is impossible to read, but because the review process is fragmented. One tool comments on tests, another comments on structure, a third comments on security, and none of them share the same output shape. The Code Review family fixes that by giving agents one review surface and a coordinated set of sibling skills.

"We wanted review output that is consistent, ranked, and useful to the next engineer," said the CodeReview 團隊. "The point is to reduce guesswork, not to pretend review output is a release gate."

The front door itself runs a built-in **AST-based review** (`review-cli review`, for Go/Python/TypeScript/C#) as the primary deterministic pass. Around it, the family combines graph-backed structural analysis, maintainability guidance, test-quality inspection, test-design generation, offline security preflight, and Sonar ingestion. Those deeper passes are delivered by **separately-installed sibling skills** that `code-review` orchestrates but does not contain, so the combined capability assumes those siblings are installed alongside it. The result is a review workflow that is more deterministic, more reusable, and easier to hand off.

Code Review is available as a packageable skill family rooted at `skills/code-review/`, with companion skills installed alongside it when the environment needs deeper review coverage.

## FAQ

### Who is this for?

Teams that need review help on real repositories, especially when code structure, tests, and security need to be analyzed together.

### Is this a runtime readiness gate?

No. It is static analysis and bounded-context tooling. Runtime readiness still comes from the consuming repo's review and runtime evidence.

### Why separate `test-quality-reviewer` from `test-design-generator`?

One judges existing tests; the other generates candidate tests. Keeping them separate preserves the distinction between diagnosis and design. This matters because teams often confuse "we need more tests" with "our current tests are weak in these specific ways." The two actions have different costs and different owners.

### Why include `sonarqube-bridge`?

Because Sonar issues are often the same review conversation in a different source system. Bridging them into the same ranking model keeps the handoff coherent.

### Why separate `code-refactoring-advisor` from `code-review`?

Because naming a refactor move is not the same as making the review judgment. The advisor helps the next engineer act, but it should not replace the reviewer's explanation of why the smell matters.

### Are `capability-mapper` and `code-summarizer` core family members?

No. They are supporting tooling that the family can orchestrate when graph or summary context is useful.

### What should be packaged with this family?

At minimum, package `skills/code-review/`, its sibling review skills, and the supporting tooling if the target environment expects graph or summary enrichment.

## Evidence And Claim Boundary

This README describes the review capability bundle. It does not claim that a consuming repository is production-ready, demo-ready, or free of regressions. Those claims belong to the consuming repo's own review artifacts and runtime evidence.

## Maintenance

When the helper skill list, invocation contract, or packaging expectations change, update this README using `GENERATION_GUIDE.md`.
