---
name: scrum-developer-skill
version: 1.0.0
description: Execute coding tasks from Scrum Master using TDD workflow and existing skills
author: AI Multi-Agent Coordinator Team
---

# Scrum Developer Skill

執行 Scrum Master 分配的開發任務，使用 TDD workflow 和現有 skills 組合。

## 使用時機

在 opencode-sandbox-station workload 中執行 Asynq queue 拉取的 coding 任務。

---

## Workflow

```
1. Understand Task (理解任務)
   ├─ 解析 Task JSON spec
   ├─ 識別需求和驗收標準
   └─ 規劃實作步驟

2. Design Solution (設計方案)
   ├─ 選擇架構模式
   ├─ 設計資料結構
   └─ 規劃測試策略

3. Implement (TDD 實作)
   ├─ RED: 寫失敗測試
   ├─ GREEN: 最小實作
   └─ REFACTOR: 重構優化

4. Quality Check (品質檢查)
   ├─ 執行測試
   ├─ 執行 EDD 評估 (Eval Check)
   ├─ 安全審查
   └─ 程式碼規範檢查

5. Document (文件生成)
   ├─ 更新技術文件
   ├─ 記錄 Lesson Learned
   └─ 準備交付物
```

---

## Phase 1: Understand Task

### 輸入
```json
{
  "id": "task-001",
  "epic_id": "epic-001",
  "title": "Implement user authentication",
  "description": "...",
  "spec": {
    "requirements": [...],
    "acceptance_criteria": [...],
    "dependencies": [...]
  },
  "iteration": 1
}
```

### 步驟

1. **解析 Task Spec**
   ```bash
   # 環境變數由 Sandbox Station 注入
   echo "Task ID: $TASK_ID"
   echo "Workload ID: $WORKLOAD_ID"
   cat task-spec.json | jq .
   ```

2. **識別需求** (使用 ba-analyst-skill 概念)
   - 功能需求 (Functional Requirements)
   - 非功能需求 (NFRs)
   - 驗收標準 (Acceptance Criteria)
   - 依賴關係 (Dependencies)

3. **規劃步驟** (使用 kiro-skill workflow)
   - 拆解為子任務
   - 識別風險
   - 估算工作量
   - 若 target surface 位於 repo-owned `skills/`，先確認這次變更是否來自 active spec task / approved change candidate，而不是 ad-hoc direct edit

### 輸出
```markdown
# Task Understanding Report

## Requirements
- FR1: User can login with email/password
- NFR1: Response time < 200ms
- NFR2: Password must be hashed with bcrypt

## Acceptance Criteria
- [ ] Login endpoint returns JWT token
- [ ] Invalid credentials return 401
- [ ] Rate limiting: 5 attempts per minute

## Implementation Plan
1. Create User model (ent schema)
2. Implement authentication service
3. Add login endpoint
4. Write integration tests
```

---

## Phase 2: Design Solution

### 使用 Skills
- `backend-patterns` — 選擇架構模式
- `golang-patterns` — Go 程式碼模式
- `postgres-patterns` — 資料庫設計
- `solution-designer-skill` — 解決方案設計

### 步驟

1. **選擇架構模式**
   ```go
   // Repository Pattern (from backend-patterns)
   type UserRepository interface {
       FindByEmail(ctx context.Context, email string) (*User, error)
       Create(ctx context.Context, user *User) error
   }
   
   // Service Layer (from backend-patterns)
   type AuthService struct {
       userRepo UserRepository
       jwtSecret string
   }
   ```

2. **設計資料結構**
   ```go
   // ent/schema/user.go (from postgres-patterns)
   type User struct {
       ent.Schema
   }
   
   func (User) Fields() []ent.Field {
       return []ent.Field{
           field.String("email").Unique(),
           field.String("password_hash"),
           field.Time("created_at").Default(time.Now),
       }
   }
   ```

3. **規劃測試策略** (from golang-testing)
   - Unit tests: Service logic
   - Integration tests: Repository + DB
   - E2E tests: HTTP endpoint

### 輸出
```markdown
# Design Document

## Architecture
- Pattern: Repository + Service Layer
- Database: PostgreSQL (ent ORM)
- Authentication: JWT (HS256)

## Data Model
- User: email, password_hash, created_at

## Test Strategy
- Unit: AuthService.Login()
- Integration: UserRepository with real DB
- E2E: POST /api/auth/login
```

---

## Phase 3: Implement (TDD)

### 使用 Skills
- `tdd-workflow` — TDD 流程
- `golang-patterns` — Go 實作模式
- `golang-testing` — 測試模式

### TDD Cycle

#### RED: 寫失敗測試

```go
// internal/auth/service_test.go
func TestAuthService_Login_Success(t *testing.T) {
    // Arrange
    repo := &mockUserRepo{
        users: map[string]*User{
            "test@example.com": {
                Email: "test@example.com",
                PasswordHash: hashPassword("password123"),
            },
        },
    }
    svc := NewAuthService(repo, "secret")
    
    // Act
    token, err := svc.Login(context.Background(), "test@example.com", "password123")
    
    // Assert
    require.NoError(t, err)
    assert.NotEmpty(t, token)
}
```

#### GREEN: 最小實作

```go
// internal/auth/service.go
func (s *AuthService) Login(ctx context.Context, email, password string) (string, error) {
    user, err := s.userRepo.FindByEmail(ctx, email)
    if err != nil {
        return "", ErrInvalidCredentials
    }
    
    if !checkPassword(password, user.PasswordHash) {
        return "", ErrInvalidCredentials
    }
    
    return s.generateJWT(user.ID)
}
```

#### REFACTOR: 重構優化

```go
// 提取常數
const (
    ErrInvalidCredentials = errors.New("invalid credentials")
    JWTExpiration = 24 * time.Hour
)

// 提取函數
func (s *AuthService) validateCredentials(ctx context.Context, email, password string) (*User, error) {
    user, err := s.userRepo.FindByEmail(ctx, email)
    if err != nil {
        return nil, ErrInvalidCredentials
    }
    
    if !checkPassword(password, user.PasswordHash) {
        return nil, ErrInvalidCredentials
    }
    
    return user, nil
}
```

對於採用 TDD 的任務，REFACTOR 不應只是示意範例；若上游 task spec / `tasks.md` 缺少 REFRACTOR 規劃，worker 應將其視為 planning gap 並在 handoff / report 中指出，而不是默默省略。

### 執行測試

```bash
# Unit tests
go test ./internal/auth/... -v

# Integration tests
go test ./internal/auth/... -tags=integration -v

# Coverage
go test ./internal/auth/... -cover
```

---

## Phase 4: Quality Check

### 使用 Skills
- `security-review` — 安全審查
- `coding-standards` — 程式碼規範
- `eval-harness` — 執行 EDD 評估與防退化檢查

### 檢查項目

#### 1. EDD 評估與驗證 (Eval Check)

作為 Definition of Done (DoD) 的核心部分，開發完成後必須透過 EDD (Eval-Driven Development) 進行能力評估與防退化檢查：

```bash
# 執行 EDD 驗證 (參考 eval-harness skill)
# 確保 Capability Evals 與 Regression Evals 皆通過
/eval check <feature-name>

# 預期輸出範例
# EVAL REPORT: <feature-name>
# Capability: 5/5 passed (pass@3: 100%)
# Regression: 3/3 passed (pass^3: 100%)
# Status: SHIP IT
```

#### 2. 安全審查 (OWASP Top 10)

```bash
# 檢查清單
- [ ] 密碼使用 bcrypt hash (cost >= 12)
- [ ] JWT secret 從環境變數讀取
- [ ] Rate limiting 防止暴力破解
- [ ] 輸入驗證 (email format)
- [ ] SQL injection 防護 (使用 ORM)
- [ ] 敏感資料不記錄到 log
```

#### 3. 程式碼規範

```bash
# 執行 linter
golangci-lint run ./internal/auth/...

# 格式化
gofmt -w ./internal/auth/

# 檢查
go vet ./internal/auth/...
```

#### 4. 測試覆蓋率

```bash
# 要求 >= 80%
go test ./internal/auth/... -coverprofile=coverage.out
go tool cover -func=coverage.out
```

#### 5. Review Handoff Readiness

完成 Quality Check 後，worker 應明確判斷是否已達到 **review handoff readiness**，而不是自行宣告最終完成：

- tests / eval / lint / security evidence 是否可讀回
- diff / artifact refs 是否已整理
- 是否涉及 shared workflow / global skill / authority boundary 變更
- 是否需要由 reviewer / QA lane 或 spec-local `review.md` 給出 formal verdict
- 若本次工作宣稱採用 TDD，是否已完成並證明 `REFACTOR` 階段，而不是只停在 GREEN
- 若本次工作屬於 improvement / governance / completed-baseline follow-up，是否已標示 candidate owner / current lane（既有 active spec、CR overlay、或 issue-log candidate）
- 若本次工作影響 critical tests 或 open CR，是否已說明 impacted tests / evidence freshness posture，而不是沿用舊綠燈 snapshot

若以上條件尚未滿足，狀態仍應視為 `running` 或 `review_pending`，不可自我宣告 readiness verdict。

---

## Phase 5: Document

### 使用 Skills
- `spec-writer-skill` — 技術文件
- Lesson Learned CLI (from sandbox-station)

### 文件生成

#### 1. API 文件

```markdown
# Authentication API

## POST /api/auth/login

**Request**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response** (200):
```json
{
  "token": "eyJhbGc...",
  "expires_at": "2026-03-05T12:00:00Z"
}
```

**Errors**:
- 401: Invalid credentials
- 429: Too many requests
```

#### 2. Lesson Learned

```bash
# 記錄經驗教訓
lesson-learned record \
  --workload-id $WORKLOAD_ID \
  --type lesson-learned \
  --title "JWT secret management" \
  --lesson "Always load JWT secret from environment variables, never hardcode"
```

#### 3. 交付物

```
artifacts/
├── code/
│   ├── internal/auth/service.go
│   ├── internal/auth/service_test.go
│   └── ent/schema/user.go
├── docs/
│   ├── api.md
│   └── design.md
├── tests/
│   └── coverage.out
└── lesson-learned.md
```

對於 shared workflow / global skill / governance 類任務，交付物還應至少包含：

- changed file list
- evidence refs（tests / eval / readback / reports）
- handoff summary（交給誰 review、為何需要 review）
- candidate owner / lane status（continue active spec / CR overlay / issue-log candidate）
- impacted tests / CR freshness note（若適用）

---

## 環境變數

Sandbox Station 自動注入：

```bash
TASK_ID=task-001                    # Task ID
WORKLOAD_ID=ext-task-task-001       # Workload ID
CONTROLLER_API_URL=http://...:19080 # Controller API
GIT_REPO_URL=https://github.com/... # Git repository (optional)
```

---

## 錯誤處理

### 常見錯誤

1. **測試失敗** → 修正程式碼，重新測試
2. **安全問題** → 修正漏洞，記錄 Lesson Learned
3. **覆蓋率不足** → 補充測試
4. **Lint 錯誤** → 修正程式碼風格

### 回報狀態

Sandbox Station 自動回報：
- `running` — 執行中
- `review_pending` — 等待 QC 審查
- `failed` — 失敗 (附錯誤訊息)

補充規則：

- `review_pending` 代表 worker 已完成本地實作與 evidence 整理，等待外部 review lane / spec-local `review.md` 裁決
- worker 不應把 `review_pending` 或 green tests 等同於最終 readiness verdict
- worker 不應自行建立新 spec；若找不到既有 owner，僅可回報 issue-log candidate 與 supporting evidence，交由上游 lane 決定

---

## 參考 Skills

### 核心
- `kiro-skill` — SDD workflow
- `golang-patterns` — Go 程式碼模式
- `golang-testing` — Go 測試模式
- `tdd-workflow` — TDD 流程

### 輔助
- `backend-patterns` — 架構模式
- `postgres-patterns` — 資料庫設計
- `security-review` — 安全審查
- `coding-standards` — 程式碼規範
- `spec-writer-skill` — 技術文件
- `ba-analyst-skill` — 需求分析
- `solution-designer-skill` — 解決方案設計

---

## 最佳實踐

1. **Always TDD** — 先寫測試，再寫程式碼
2. **Minimal Implementation** — 最小可行實作
3. **Security First** — 安全優先
4. **Document Everything** — 記錄所有決策
5. **Learn from Mistakes** — 記錄 Lesson Learned

---

**版本**: 1.0.0  
**最後更新**: 2026-03-04
