# The Spec Master Method — Methodology Diagram / 方法論圖

> Renders on GitHub automatically. The skills are color-grouped into the three layers
> of the method: **govern & route**, **deliver**, and **verify (left-shift)**.
> 在 GitHub 上會自動渲染。skills 依方法的三層上色：**治理與路由**、**交付**、**驗證（左移）**。

## 1. Skill handoff across the six SDD phases / 六階段中的 skill 交棒

```mermaid
flowchart TD
    REQ["Request / 請求"] --> SM["spec-master<br/>route by authority surface<br/>依權威面路由"]

    SM -->|"new feature / complex fix<br/>新功能 / 複雜修復"| P1
    SM -->|"unresolved, no safe owner<br/>未解決、無安全 owner"| IL["issue-log-manager<br/>ISSUE_LOG.md"]
    SM -->|"registry sync<br/>註冊同步"| SR["spec-registry-manager<br/>SPECS.md"]
    SM -->|"runtime alloc<br/>執行環境配置"| LI["local-infra-registry-governance"]

    subgraph SDD["spec-driven-development — 6 phases / 六階段"]
        direction TB
        P1["Phase 1 · Requirements<br/>EARS AC · YAGNI Rung 1"]
        P2["Phase 2 · Design<br/>DDD bounded contexts · Rung 2-4"]
        P3["Phase 3 · Tasks<br/>plan closeout & traceability"]
        P4["Phase 4 · Implementation<br/>TDD red/green/refactor · Rung 5-6"]
        P5["Phase 5 · Review<br/>review.md verdict"]
        P6["Phase 6 · Optimization"]
        P1 --> P2 --> P3 --> P4 --> P5 --> P6
    end

    P4 -.->|red/green/refactor| TDD["tdd-workflow"]
    P4 -.->|test cases| TDG["test-design-generator"]
    P4 -.->|rows & evidence| TR["test-registry-manager<br/>TESTS.md"]

    P5 -.->|left-shift detection| CR["code-review family<br/>refactoring-advisor · test-quality-reviewer<br/>security-risk-reviewer · sonarqube-bridge"]

    P6 --> IL
    P6 --> SR

    classDef govern fill:#284d8f,stroke:#cdd9f0,color:#fff;
    classDef deliver fill:#116b5f,stroke:#bfeee6,color:#fff;
    classDef verify fill:#9a4d14,stroke:#ffd9b8,color:#fff;

    class SM,SR,IL,LI govern;
    class P1,P2,P3,P4,P5,P6,TDD,TDG,TR deliver;
    class CR verify;
```

## 2. One-way evidence flow / 單向證據流

The method's core anti-false-green rule: evidence only flows **up** into derived summaries; derived summaries **never** sync back into upstream truth.

此方法防止 false-green 的核心規則：證據只**向上**流入衍生摘要；衍生摘要**永不**反向同步回上游真相。

```mermaid
flowchart LR
    A["ISSUE_LOG.md<br/>unresolved / 未解決"] --> B["spec artifacts & reports<br/>requirements · design · tasks · code"]
    B --> C["folder-level TESTS.md<br/>rows & evidence refs"]
    C --> D["workspace test rollup"]
    D --> E["RTM.md<br/>requirement traceability"]
    E --> F["SPECS.md<br/>stable registry summary"]

    R["review.md<br/>readiness verdict — authority"] -.owns.-> READY(("demo / release<br/>readiness"))

    F -. "must NOT sync back / 禁止反向同步" .-> B
    linkStyle 6 stroke:#c0392b,stroke-width:2px,color:#c0392b;
```

## 3. Practice → owner skill map / 實踐 → owner skill 對照

```mermaid
flowchart TB
    subgraph Practices["Classic practices / 經典實踐"]
        SDDp["SDD"]
        TDDp["TDD"]
        DDDp["DDD"]
        TMp["Test Management / 測試管理"]
        RFp["Refactoring / 重構"]
        SECp["Security left-shift / 安全左移"]
    end

    SDDp --> s1["spec-driven-development"]
    TDDp --> s2["tdd-workflow + test-design-generator"]
    DDDp --> s3["SDD Phase 2 design"]
    TMp --> s4["test-registry-manager + test-quality-reviewer"]
    RFp --> s5["code-refactoring-advisor"]
    SECp --> s6["security-risk-reviewer + code-review"]
```
