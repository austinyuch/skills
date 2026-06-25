# aclab Skills（技能合集）

**aclab** 精選的 AI agent 技能合集，專注於專業軟體開發工作流。這是一套 **agent-agnostic（不綁單一廠商）**
的合集——這些技能可在 **OpenCode**、**Claude Code** 與 **Codex**（以及其他相容 runtime）上執行，不限單一平台。

🌐 **語言：** [English](README.md) · [繁體中文](README.zh-TW.md)

> 🤖 **使用程式代理人嗎？** 請先讀 [`AGENTS.md`](AGENTS.md) — 它說明如何在本合集中導航、何時進入
> **Spec Master Method**，以及這些技能預期的路由／責任歸屬規則。

## 快速開始

把技能安裝到你的 coding agent。**不會發布到任何 registry** —— 以下每個指令都直接從這個 Git repo 解析。
挑你手邊已有的 runtime 即可。

`<agent>` = `opencode` | `claude` | `codex` | `kiro`（預設 `opencode`）。

**Node — npx / bunx（免 clone）：**
```bash
npx -y github:austinyuch/skills claude
bunx   github:austinyuch/skills codex
```

**Python — uvx / pipx（免 clone）：**
```bash
uvx --from git+https://github.com/austinyuch/skills aclab-skills claude
pipx run --spec git+https://github.com/austinyuch/skills aclab-skills codex
```

**沒有 Node/Python —— clone 後跑腳本（跨平台）：**
```bash
git clone https://github.com/austinyuch/skills.git && cd skills
bash scripts/install.sh claude       # macOS / Linux
pwsh scripts/install.ps1 claude      # Windows PowerShell
```

每個技能會安裝成 `<skill-home>/<skill-name>/`，agent 會自動載入。可用 `SKILLS_TARGET=/custom/path`
覆寫目的地。（OpenCode 使用者也可用社群工具：`npx skills@latest add austinyuch/skills`。）

### Native binaries（放在 GitHub Releases，不進 git）

少數 skill 依賴**預編譯的 native binary／模型，這些刻意不 commit 進來** —— 它們很大且依平台而異，
所以已 gitignore。這讓 `git clone`、`npx`、`uvx` 保持快速且**不需 git LFS**（沒有 git-lfs 相依、不會
拿到 pointer 假檔）。它們改用 **GitHub Releases 發佈，絕不用 git LFS。**

- **`code-review`** 使用 `review-cli-<os>-<arch>` binary（外加約 128 MB 的 embedding 模型）。安裝只會複製
  skill 的文件／腳本，**不含** binary。用 `--with-cli` 抓對應平台的 binary：

  ```bash
  npx -y github:austinyuch/skills claude --with-cli
  uvx --from git+https://github.com/austinyuch/skills aclab-skills claude --with-cli
  bash scripts/install.sh claude --with-cli       #   macOS / Linux
  pwsh scripts/install.ps1 claude -WithCli         #   Windows
  ```

  純 Python 的複核 helper —— `code-refactoring-advisor`、`test-quality-reviewer`、
  `security-risk-reviewer`、`test-design-generator` —— 不需 binary，可直接使用。模型不會被抓
  （CLI 在 graph-only 模式下不需要它）。

> 🔐 **本 repository 是 private。** `npx`／`uvx`／`git clone` **以及** `--with-cli` 下載 binary 都需要
> GitHub 驗證。`--with-cli` 透過 **`gh` CLI**（`gh auth login`）從
> [`review-cli-v0.11.0`](https://github.com/austinyuch/skills/releases/tag/review-cli-v0.11.0)
> release 抓 asset；沒有 `gh` 時會印出可直接執行的 `gh release download …` 指令。除非把 repo（或 release）
> 設為 public，否則無法匿名安裝。

## 內容總覽

| 分類 | 技能數 | 說明 |
|------|--------|------|
| **Spec Master** | 2 | 規格路由與規格驅動開發 |
| **Code Review** | 6 | 複核、品質、安全與測試工具 |
| **Scrum** | 2 | Scrum 與敏捷團隊工作流 |
| **Engineering** | 15 | 核心軟體工程工作流 |
| **Architecture** | 15 | 架構、治理與流程設計 |
| **DevOps** | 6 | DevOps、容器與基礎設施 |
| **Productivity** | 7 | 生產力、寫作與協作 |
| **Data** | 4 | 數據分析、BI 與資料庫 |
| **Domain Expert** | 1 | 領域專家知識 |
| **Creative** | 2 | 前端、設計與創意工具 |
| **Security & Compliance** | 1 | 安全複核與合規 |
| **Social Media** | 4 | 社群媒體、倡議與行銷 |
| **Tools** | 1 | 開發者工具與整合 |
| **User Experience** | 1 | 使用者檔案、手冊與互動 |
| **Project Review** | 2 | 專案複核與高管報告 |
| **UAT & Demo** | 1 | UAT 與 demo 執行工具 |

## Spec Master Method（開發方法）

> **把 DevSecOps、Scrum 與 TDD 帶進 agentic 工作流——而且不失真。**

程式代理人讓「產生程式碼」變便宜，卻沒讓「協調程式碼」變便宜。瓶頸從打字轉移到決定責任歸屬、維持證據新鮮，
以及阻止一個看似綠燈的檔案謊報 readiness。**Spec Master Method** 是一套由 **14 個可組合技能**組成的開源家族，
把五種已驗證的工程實踐移植成一個受治理、可檢視的 agentic 工作流。

| 經典實踐 | 它依然負責的任務 | Owner 技能 |
|---|---|---|
| 規格驅動開發 (SDD) | 模糊意圖 → 可追溯交付 | `spec-driven-development`（啟發自 [AWS Kiro](https://kiro.dev)） |
| 測試驅動開發 (TDD) | 改程式前先釘住行為 | `tdd-workflow` + `test-design-generator` |
| 領域驅動設計 (DDD) | 讓邊界對齊業務語言 | SDD Phase 2（bounded contexts） |
| 測試管理 | CI 綠燈 → 可稽核的風險證據 | `test-registry-manager` + `test-quality-reviewer` |
| 重構 | 在行為被保護後降低變更成本 | `code-refactoring-advisor` |

14 個技能分三層：

- **治理與路由** — `spec-master`（前門）、`spec-registry-manager`、`issue-log-manager`、`local-infra-registry-governance`、`shared-governance`
- **交付** — `spec-driven-development`（六階段生命週期）、`tdd-workflow`、`test-registry-manager`、`test-design-generator`
- **驗證（左移）** — `code-review`、`code-refactoring-advisor`、`test-quality-reviewer`、`security-risk-reviewer`、`sonarqube-bridge`

防止假綠燈的核心規則：**證據單向流動** — `ISSUE_LOG → spec 工件 → folder-level TESTS.md → workspace rollup → RTM.md → SPECS.md` — 衍生摘要永不反向同步回上游真相。

**深入閱讀：**
- 🟦 [`methodology.html`](./methodology.html) — 雙語 EN/繁中 landing page
- 📖 [`docs/agentic-delivery-methodology.md`](./docs/agentic-delivery-methodology.md) — 完整方法論文章（雙語）
- 🗺️ [`docs/methodology-diagram.md`](./docs/methodology-diagram.md) — 交棒、證據流與實踐對照圖
- 深入：[Spec Master + SDD 說帖](./skills/spec-master/index.html) · [Code Review 家族說帖](./skills/code-review/index.html)

> `spec-driven-development` 啟發自 **AWS Kiro**；YAGNI 階梯改編自 **Ponytail**（MIT）；它建立在 **Scrum**、**Agile Manifesto**、**TDD/DDD** 等之上。完整出處：[`CREDITS.md`](./CREDITS.md)。

## 技能家族

### Spec Master
- `spec-master` - 規格路由、治理與改善項分類（前門）
- `spec-driven-development` - 系統化規格生命週期：需求、設計、任務、實作、複核、優化

### Code Review
- `code-review` - 以 CLI 工具進行程式複核
- `test-quality-reviewer` - 評估測試有效性
- `code-refactoring-advisor` - 偵測程式異味並建議重構
- `test-design-generator` - 生成具體測試案例
- `security-risk-reviewer` - OWASP 安全掃描
- `sonarqube-bridge` - SonarQube 整合

### Scrum
- `scrum-master-skill` - Scrum Master 協調
- `scrum-developer-skill` - Scrum 開發者執行

## 技能分類

### Engineering（工程）
- `spec-registry-manager` - 規格目錄管理
- `code-review` - 以 CLI 工具進行程式複核
- `code-refactoring-advisor` - 偵測程式異味並建議重構
- `code-summarizer` - 檔案層級程式摘要
- `test-quality-reviewer` - 評估測試有效性
- `test-design-generator` - 生成具體測試案例
- `test-registry-manager` - 測試目錄治理
- `tdd-workflow` - 測試驅動開發
- `verification-loop` - 實作後驗證
- `eval-harness` - 評估框架
- `backend-patterns` - 後端架構模式
- `frontend-patterns` - 前端開發模式
- `coding-standards` - 通用程式規範
- `golang-patterns` - 慣用 Go 模式
- `golang-testing` - Go 測試模式
- `go-rust-optimizer` - 以 Rust 優化 Go 效能
- `node-rust-optimizer` - 以 Rust 優化 Node.js 效能
- `python-rust-optimizer` - 以 Rust 優化 Python 效能
- `sonarqube-bridge` - SonarQube 整合
- `capability-mapper` - 將程式對應到業務能力

### Architecture（架構）
- `agentic-scrum-governance` - Agentic Scrum 治理
- `shared-governance` - 共用治理規則
- `committee-decision-making` - 多 LLM 決策
- `strategic-compact` - 上下文壓縮策略
- `iterative-retrieval` - 漸進式上下文檢索
- `epic-breakdown-skill` - Epic 拆解
- `requirements-workflow-skill` - 需求管理工作流
- `workflow-skill-creator` - Workflow 技能產生器
- `continuous-learning` - 從 session 萃取模式
- `continuous-learning-v2` - 基於 instinct 的學習
- `skill-migration-workflow` - 技能遷移與比較
- `cross-agents-symlink-bridge` - 跨 agent 橋接設定
- `issue-log-manager` - Issue log 治理
- `uat-demo-agent` - UAT/Demo 計畫執行
- `uat-demo-agent-packaging` - 技能打包
- `uat-demo-target-governance-template` - 治理範本

### DevOps
- `devops-container-orchestration` - 容器編排模式
- `podman-rootless` - Podman rootless 開發
- `k8s-security-patterns` - Kubernetes 安全
- `local-infra-registry-governance` - 本地基礎設施註冊
- `container-image-janitor` - 容器映像清理
- `cross-platform-dev-scripts` - 跨平台開發腳本

### Productivity（生產力）
- `writer-skill` - 專業文件寫作
- `vibe-skill` - 快速開發工作流
- `kiro-skill` - 系統化開發工作流
- `pm-skill` - 產品管理助手
- `prd-skill` - PRD 文件生成
- `name-skill` - 程式命名助手
- `find-skills` - 技能探索

### Data（數據）
- `clickhouse-io` - ClickHouse 資料庫模式
- `postgres-patterns` - PostgreSQL 模式
- `database-modernization-strangler` - 遺留資料庫現代化
- `taiwan-civic-budget-tracker` - 政府預算追蹤

### Domain Expert（領域專家）
- `microsoft-foundry` - Azure AI Foundry 部署

### Creative（創意）
- `ui-skill` - B2B 供應鏈互動 HTML
- `shadcn` - shadcn/ui 元件管理

### Security & Compliance（安全與合規）
- `security-review` - 安全複核檢查清單
- `security-risk-reviewer` - OWASP 安全掃描

### Social Media（社群媒體）
- `social-media-platforms` - 社群媒體內容優化
- `social-post-generator` - 社群貼文生成
- `victim-rights-news-tracker` - 倡議新聞追蹤
- `brand-guidelines-naelt` - NAELT 品牌指南

> 另外隨附：`NPO-marketing-guide.md`（standalone 參考文件，會與 skills 一併安裝）。

### Tools（工具）
- `local-llm-agent-migrator` - 本地 LLM agent 遷移

### Scrum
- `scrum-master-skill` - Scrum Master 協調
- `scrum-developer-skill` - Scrum 開發者執行

### User Experience（使用者體驗）
- `user-manual-skill` - 使用者手冊生成

### Project Review（專案複核）
- `project-review-skill` - 高管專案複核
- `project-review-naelt` - NAELT 專案複核

### UAT & Demo
- `uat-demo-agent` - UAT/Demo 計畫執行

## 參與貢獻

歡迎 PR —— 見 [CONTRIBUTING.md](CONTRIBUTING.md)。重點：先裝 hooks
（`bash scripts/install-git-hooks.sh`），保持 manifest／README／twins 同步，並確認
`bash scripts/ci-checks.sh` 通過（與 CI 相同的檢查）。請遵守 [Code of Conduct](CODE_OF_CONDUCT.md)；
安全問題請依 [SECURITY.md](SECURITY.md) 回報。

## 授權與致謝

本 repository 以 **MIT** 授權（見根目錄 [LICENSE](LICENSE)），**唯一例外是 code-review 家族**，
採 **Apache-2.0**。這六個 skill 各自附 `LICENSE` + `NOTICE`：

- Apache-2.0：`code-review`、`code-refactoring-advisor`、`test-quality-reviewer`、
  `test-design-generator`、`security-risk-reviewer`、`sonarqube-bridge`（Code Review System）。
- MIT（根目錄）：其餘全部，包含 `capability-mapper` 與 `code-summarizer`。

> **注意：** 取材自 Anthropic `anthropics/skills`（以及專有的 `docx`/`pdf`/`pptx`/`xlsx`）與 Giant 公司資產的技能，
> 已**自本合集移除**。方法論仍以概念影響的形式致謝其來源——**AWS Kiro**、**Ponytail**（MIT）、**gstack**（MIT）、
> **mattpocock/skills**（MIT）、**Everything Claude Code**（MIT）、**Scrum Guide**、**Agile Manifesto** 等。
> 完整出處與推薦上游連結見 [**CREDITS.md**](CREDITS.md)。
