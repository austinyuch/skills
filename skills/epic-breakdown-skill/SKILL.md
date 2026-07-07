---
name: epic-breakdown-skill
description: Epic 拆解專家。將 Epic 拆解為可執行的 Tasks，遵循 INVEST/DEEP 原則，支援 2-4 並行 workers，包含 contract 定義和整合測試。調用 ba-analyst-skill 進行需求分析，確保 task 品質。
---

# Epic Breakdown Skill

## 角色定位

Epic Breakdown Agent - 將 Epic 拆解為可執行 Tasks 的專家

## 核心職責

1. **需求分析**: 調用 ba-analyst-skill 分析 Epic
2. **Task 拆解**: 遵循 INVEST/DEEP 原則
3. **並行規劃**: 2-4 workers 並行執行
4. **測試策略**: Contract + Integration Tests
5. **依賴管理**: DAG 依賴關係

## 拆解原則

### INVEST (User Stories)
- **Independent**: 獨立可執行
- **Negotiable**: 實作細節可協商
- **Valuable**: 每個 task 有價值
- **Estimable**: 明確範圍
- **Small**: 1-2 天完成
- **Testable**: 可測試

### DEEP (Backlog)
- **Detailed appropriately**: 近期 task 更詳細
- **Estimated**: 相對大小 (S/M/L)
- **Emergent**: 隨學習演進
- **Prioritized**: 關鍵路徑優先

> 若在拆解過程中產生 deferred / emergent slices，應流向 workspace backlog mechanism（先 summary-mode，必要時再抽出 `PRODUCT_BACKLOG.md`），而不是混入 spec-level truth 或 runtime readiness 結論。

## Task 結構

### 必要 Task 類型

1. **Contract Definition** (index 0)
   - Role: Coder
   - 定義 API/Interface contracts
   - 無依賴

2. **Implementation Tasks** (index 1-4)
   - Role: Coder
   - 2-4 個並行 tasks
   - 依賴 contract (depends_on: ["0"])

3. **Integration Tests** (index 5)
   - Role: QA_Engineer
   - 跨元件測試
   - 依賴所有 implementation

4. **QC Review** (index 6)
   - Role: QC_Reviewer
   - 品質審查
   - 依賴 integration tests

## 工作流程

### Phase 1: 需求分析
```bash
# 調用 ba-analyst-skill 分析 Epic
kiro-skill ba-analyst-skill \
  --input "Epic: {title}\nContext: {business_context}\nAC: {acceptance_criteria}"
```

**輸出**: 
- 問題空間分析
- 功能需求清單
- 非功能需求
- 驗收標準 (BDD)

### Phase 2: Task 拆解
基於 BA 分析結果，拆解為 tasks：

**Contract Task**:
```json
{
  "title": "Define {component} API contracts",
  "role_needed": "Coder",
  "payload_context": {
    "description": "Define REST API contracts with OpenAPI spec",
    "acceptance_criteria": "All endpoints, schemas, error codes documented",
    "technical_notes": "Use OpenAPI 3.0, include examples",
    "test_requirements": "Contract tests for all endpoints"
  },
  "depends_on": [],
  "estimated_effort": "S"
}
```

**Implementation Tasks** (2-4 並行):
```json
{
  "title": "Implement {feature} endpoint",
  "role_needed": "Coder",
  "payload_context": {
    "description": "Implement POST /endpoint with validation",
    "acceptance_criteria": "Endpoint works per contract, tests pass",
    "technical_notes": "Use TDD workflow, follow contract",
    "test_requirements": "Unit + integration tests, >80% coverage"
  },
  "depends_on": ["0"],
  "estimated_effort": "M"
}
```

**Integration Test**:
```json
{
  "title": "Integration tests for {epic}",
  "role_needed": "QA_Engineer",
  "payload_context": {
    "description": "E2E tests for complete flow",
    "acceptance_criteria": "All scenarios covered, tests pass",
    "technical_notes": "Use test database, clean up after",
    "test_requirements": "Happy path + error cases"
  },
  "depends_on": ["1", "2", "3", "4"],
  "estimated_effort": "M"
}
```

**QC Review**:
```json
{
  "title": "QC review for {epic}",
  "role_needed": "QC_Reviewer",
  "payload_context": {
    "description": "Review code quality, security, coverage",
    "acceptance_criteria": "Standards met, >80% coverage, no vulnerabilities",
    "technical_notes": "Check OWASP Top 10, code standards",
    "test_requirements": "All tests passing"
  },
  "depends_on": ["5"],
  "estimated_effort": "S"
}
```

### Phase 3: 依賴分析
生成 DAG：
```
Contract (0)
    ├─> Impl 1 (1)
    ├─> Impl 2 (2)
    ├─> Impl 3 (3)
    └─> Impl 4 (4)
            └─> Integration (5)
                    └─> QC (6)
```

### Phase 4: 輸出 JSON
```json
[
  { "title": "...", "depends_on": [] },
  { "title": "...", "depends_on": ["0"] },
  { "title": "...", "depends_on": ["0"] },
  { "title": "...", "depends_on": ["1", "2"] },
  { "title": "...", "depends_on": ["3"] }
]
```

## 調用方式

### 從 Coordinator
```go
// internal/breakdown/llm.go
func BreakdownEpic(epic *ent.Epic) ([]Task, error) {
    // 1. 準備 prompt
    prompt := fmt.Sprintf(`
Epic: %s
Context: %s
Acceptance Criteria: %s

Use epic-breakdown-skill to break down into tasks.
Follow INVEST/DEEP principles.
Include contract definition, 2-4 parallel implementations, integration tests, QC review.
Return JSON array only.
`, epic.Title, epic.BusinessContext, epic.AcceptanceCriteria)

    // 2. 調用 LLM (kiro-skill)
    result := kiroSkill.Execute("epic-breakdown-skill", prompt)
    
    // 3. Parse JSON
    var tasks []Task
    json.Unmarshal(result, &tasks)
    
    return tasks, nil
}
```

### 從 CLI
```bash
kiro-skill epic-breakdown-skill \
  --epic-title "User Authentication" \
  --business-context "Secure auth with JWT" \
  --acceptance-criteria "Register, login, logout"
```

## 品質檢查

### DoR (Definition of Ready)
- [ ] Epic 有明確的 business context
- [ ] Acceptance criteria 清楚
- [ ] 非功能需求已識別
- [ ] 技術可行性已確認

### DoD (Definition of Done)
- [ ] 6-8 個 tasks 已生成
- [ ] Contract task 在 index 0
- [ ] 2-4 個並行 implementation tasks
- [ ] Integration test 已包含
- [ ] QC review 已包含
- [ ] 依賴關係正確 (DAG)
- [ ] 每個 task 有明確的 acceptance criteria

## 範例

### Input Epic
```
Title: User Authentication System
Business Context: Implement secure user authentication with JWT tokens for the web application
Acceptance Criteria:
- Users can register with email/password
- Users can login and receive JWT token
- Users can logout and invalidate token
- Protected endpoints require valid token
```

### Output Tasks
```json
[
  {
    "title": "Define authentication API contracts",
    "role_needed": "Coder",
    "payload_context": {
      "description": "Define REST API contracts for /register, /login, /logout, /verify endpoints with OpenAPI 3.0 spec",
      "acceptance_criteria": "OpenAPI spec complete with all endpoints, request/response schemas, error codes, and examples",
      "technical_notes": "Use JWT for tokens (HS256), bcrypt for passwords (cost 12), include rate limiting specs",
      "test_requirements": "Contract tests for all endpoints using Pact or similar"
    },
    "depends_on": [],
    "estimated_effort": "S"
  },
  {
    "title": "Implement user registration endpoint",
    "role_needed": "Coder",
    "payload_context": {
      "description": "Implement POST /api/v1/auth/register with email validation, password hashing, and user creation in PostgreSQL",
      "acceptance_criteria": "Users can register with valid email/password, passwords hashed with bcrypt, duplicate emails rejected with 409, validation errors return 400",
      "technical_notes": "Use bcrypt cost 12, validate email format (RFC 5322), min password length 8, store in users table",
      "test_requirements": "Unit tests for validation logic, integration tests for DB operations, >80% coverage"
    },
    "depends_on": ["0"],
    "estimated_effort": "M"
  },
  {
    "title": "Implement login endpoint with JWT generation",
    "role_needed": "Coder",
    "payload_context": {
      "description": "Implement POST /api/v1/auth/login with credential verification and JWT token generation",
      "acceptance_criteria": "Valid credentials return 200 with JWT token, invalid credentials return 401, token includes user_id and expires in 24h",
      "technical_notes": "JWT with HS256, secret from env, include user_id in claims, set exp claim to 24h from now",
      "test_requirements": "Unit tests for token generation, integration tests for auth flow, test token expiry"
    },
    "depends_on": ["0"],
    "estimated_effort": "M"
  },
  {
    "title": "Implement logout with token blacklist",
    "role_needed": "Coder",
    "payload_context": {
      "description": "Implement POST /api/v1/auth/logout with token blacklist in Redis, and middleware to check blacklist",
      "acceptance_criteria": "Logged out tokens are rejected with 401, blacklist entries expire after token TTL, middleware checks blacklist on protected routes",
      "technical_notes": "Use Redis SET with TTL matching JWT exp claim, middleware extracts token and checks Redis before validating",
      "test_requirements": "Integration tests for logout flow, test blacklist expiry, test middleware rejection"
    },
    "depends_on": ["0"],
    "estimated_effort": "M"
  },
  {
    "title": "Implement token verification middleware",
    "role_needed": "Coder",
    "payload_context": {
      "description": "Implement middleware to verify JWT tokens on protected endpoints, check signature, expiry, and blacklist",
      "acceptance_criteria": "Valid tokens allow access, expired/invalid/blacklisted tokens return 401, middleware can be applied to any route",
      "technical_notes": "Extract token from Authorization header (Bearer scheme), verify signature and claims, check Redis blacklist",
      "test_requirements": "Unit tests for token validation, integration tests with protected endpoints"
    },
    "depends_on": ["0"],
    "estimated_effort": "S"
  },
  {
    "title": "Integration tests for complete auth flow",
    "role_needed": "QA_Engineer",
    "payload_context": {
      "description": "E2E tests for complete authentication flow: register → login → access protected endpoint → logout → verify token invalid",
      "acceptance_criteria": "All auth scenarios covered: success paths, error cases (invalid credentials, expired token, blacklisted token), edge cases (malformed token, missing header)",
      "technical_notes": "Use test database and Redis, clean up after each test, use real HTTP requests",
      "test_requirements": "Cover happy path, all error cases, security edge cases, >90% scenario coverage"
    },
    "depends_on": ["1", "2", "3", "4"],
    "estimated_effort": "M"
  },
  {
    "title": "QC review for authentication system",
    "role_needed": "QC_Reviewer",
    "payload_context": {
      "description": "Review code quality, security practices, test coverage, and OWASP compliance for authentication system",
      "acceptance_criteria": "Code follows Go standards, OWASP Top 10 addressed (especially A01:Broken Access Control, A02:Cryptographic Failures, A07:Identification and Authentication Failures), test coverage >80%, no high/critical vulnerabilities",
      "technical_notes": "Check for: SQL injection, XSS, password security (bcrypt cost, no plaintext), JWT security (strong secret, proper validation), rate limiting, input validation",
      "test_requirements": "All tests passing, security scan clean (gosec, trivy), coverage report >80%"
    },
    "depends_on": ["5"],
    "estimated_effort": "S"
  }
]
```

## 參考 Skills

- **ba-analyst-skill**: 需求分析
- **requirements-workflow-skill**: 工作流程編排
- **scrum-developer-skill**: Task 執行
- **scrum-master-skill**: 協調管理
