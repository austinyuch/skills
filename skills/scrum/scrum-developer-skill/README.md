# Scrum Developer Skill

執行 Scrum Master 分配的開發任務。

## 結構

```
scrum-developer-skill/
├── SKILL.md              # 主要 skill 定義
├── references/           # 引用的現有 skills
│   ├── golang-patterns/
│   ├── golang-testing/
│   ├── tdd-workflow/
│   ├── backend-patterns/
│   ├── postgres-patterns/
│   └── security-review/
├── phases/               # 執行階段 (未來擴展)
└── scripts/
    └── execute-task.sh   # 任務執行腳本
```

## 使用方式

### 在 Sandbox Station Workload 中

```bash
# 環境變數由 Sandbox Station 注入
export TASK_ID=task-001
export WORKLOAD_ID=ext-task-task-001
export CONTROLLER_API_URL=http://controller:19080

# 執行任務
cd /home/agent/workspace
./execute-task.sh task-spec.json
```

### Workflow

1. **Understand Task** — 解析 Task spec
2. **Design Solution** — 設計架構和資料結構
3. **Implement (TDD)** — RED → GREEN → REFACTOR
4. **Quality Check** — 測試、安全審查、程式碼規範
5. **Document** — 生成文件、記錄 Lesson Learned

## 引用的 Skills

- `golang-patterns` — Go 程式碼模式
- `golang-testing` — Go 測試模式
- `tdd-workflow` — TDD 流程
- `backend-patterns` — 架構模式
- `postgres-patterns` — 資料庫設計
- `security-review` — 安全審查

## 整合

此 skill 會被複製到 `opencode-worker-agent` Docker image 的 `/tmp/agent-config/.config/opencode/skills/` 目錄。

## 版本

- **1.0.0** (2026-03-04) — 初始版本
