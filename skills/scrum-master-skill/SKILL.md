---
name: scrum-master-skill
version: 1.0.0
description: Coordinate Epic breakdown, task dispatch, QC review, and team collaboration
author: AI Multi-Agent Coordinator Team
---

# Scrum Master Skill

協調 Epic 拆解、Task 派發、QC 審查和團隊協作。

## 使用時機

在 Scrum Master/Coordinator 服務中使用，管理整個開發流程。

---

## Workflow

```
Epic Received
    ↓
1. Breakdown Epic → Tasks (DAG)
    ↓
2. Dispatch Tasks → Workers
    ↓
3. Monitor Progress (Heartbeat)
    ↓
4. QC Review (Pass/Fail)
    ↓
5. Handle Clarification (Auto/HITL)
    ↓
6. Extract Lessons (Retro)
    ↓
Epic Completed
```

---

## Phase 1: Breakdown Epic

### 輸入
```json
{
  "id": "epic-001",
  "title": "User Authentication System",
  "description": "Implement complete user authentication",
  "requirements": [
    "User can register with email/password",
    "User can login and receive JWT token",
    "Password must be securely hashed"
  ]
}
```

### 使用 LLM 拆解

```go
// internal/breakdown/engine.go
func (e *Engine) BreakdownEpic(ctx context.Context, epic *Epic) ([]*Task, error) {
    prompt := fmt.Sprintf(`
Break down this Epic into Tasks with dependencies:

Epic: %s
Requirements:
%s

Output JSON array of tasks with:
- id: unique task ID
- title: task title
- description: detailed description
- dependencies: array of task IDs this depends on
- estimated_hours: estimated hours
`, epic.Title, strings.Join(epic.Requirements, "\n"))

    response := e.llm.Generate(ctx, prompt)
    return parseTasksFromJSON(response)
}
```

### 建立 DAG

```go
// internal/breakdown/dag.go
func (s *Scheduler) BuildDAG(tasks []*Task) (*DAG, error) {
    dag := NewDAG()
    
    for _, task := range tasks {
        dag.AddNode(task.ID, task)
        for _, depID := range task.Dependencies {
            dag.AddEdge(depID, task.ID)
        }
    }
    
    if dag.HasCycle() {
        return nil, ErrCyclicDependency
    }
    
    return dag, nil
}
```

### 輸出
```json
[
  {
    "id": "task-001",
    "title": "Create User model",
    "dependencies": [],
    "estimated_hours": 2
  },
  {
    "id": "task-002",
    "title": "Implement authentication service",
    "dependencies": ["task-001"],
    "estimated_hours": 4
  },
  {
    "id": "task-003",
    "title": "Add login endpoint",
    "dependencies": ["task-002"],
    "estimated_hours": 3
  }
]
```

---

## Phase 2: Dispatch Tasks

### 選擇可派發的 Tasks

```go
// internal/breakdown/dag.go
func (s *Scheduler) GetDispatchable(dag *DAG) []*Task {
    var dispatchable []*Task
    
    for _, node := range dag.Nodes {
        if node.Status == StatusPending && s.allDependenciesCompleted(node) {
            dispatchable = append(dispatchable, node.Task)
        }
    }
    
    return dispatchable
}
```

### 推送到 Asynq Queue

```go
// internal/queue/producer.go
func (p *Producer) EnqueueTask(ctx context.Context, task *Task) error {
    payload, _ := json.Marshal(task)
    
    asynqTask := asynq.NewTask(
        "coding:execute",
        payload,
        asynq.Queue("coding"),
        asynq.MaxRetry(3),
    )
    
    return p.client.EnqueueContext(ctx, asynqTask)
}
```

### 更新狀態

```go
// internal/repository/task_repo.go
func (r *TaskRepo) UpdateStatus(ctx context.Context, taskID string, status TaskStatus) error {
    return r.db.Task.
        UpdateOneID(taskID).
        SetStatus(status).
        SetUpdatedAt(time.Now()).
        Exec(ctx)
}
```

---

## Phase 3: Monitor Progress

### 心跳檢查

```go
// internal/actions/heartbeat.go
func (s *Service) CheckHeartbeats(ctx context.Context) error {
    // 查詢超時的 Tasks
    timeout := time.Now().Add(-5 * time.Minute)
    tasks, err := s.taskRepo.FindStaleHeartbeats(ctx, timeout)
    
    for _, task := range tasks {
        // 標記為 timeout
        s.taskRepo.UpdateStatus(ctx, task.ID, StatusTimeout)
        
        // 通知 HITL
        s.notifyHITL(ctx, task, "Task heartbeat timeout")
    }
    
    return nil
}
```

### 狀態追蹤

```go
// internal/statemachine/machine.go
func (m *Machine) Transition(ctx context.Context, taskID string, event Event) error {
    task, _ := m.repo.FindByID(ctx, taskID)
    
    newStatus, err := m.getNextStatus(task.Status, event)
    if err != nil {
        return err
    }
    
    return m.repo.UpdateStatus(ctx, taskID, newStatus)
}
```

---

## Phase 4: QC Review

### QA Plan 生成

```go
// internal/qaqc/planner.go
func (p *Planner) GenerateQAPlan(ctx context.Context, task *Task) (*TestPlan, error) {
    prompt := fmt.Sprintf(`
Generate QA test plan for:

Task: %s
Acceptance Criteria:
%s

Output JSON with:
- unit_tests: array of unit test descriptions
- integration_tests: array of integration test descriptions
- e2e_tests: array of E2E test descriptions
`, task.Title, task.AcceptanceCriteria)

    response := p.llm.Generate(ctx, prompt)
    return parseTestPlan(response)
}
```

### QC 檢查

```go
// internal/qaqc/checker.go
func (c *Checker) CheckQuality(ctx context.Context, task *Task) (*QCResult, error) {
    // 1. 執行測試
    testResult := c.runTests(ctx, task)
    
    // 2. 檢查覆蓋率
    coverage := c.checkCoverage(ctx, task)
    
    // 3. 安全審查
    securityIssues := c.securityScan(ctx, task)
    
    // 4. 程式碼規範
    lintIssues := c.lintCheck(ctx, task)
    
    return &QCResult{
        Pass: testResult.Pass && coverage >= 80 && len(securityIssues) == 0,
        TestResult: testResult,
        Coverage: coverage,
        SecurityIssues: securityIssues,
        LintIssues: lintIssues,
    }
}
```

### Agentic Review Trigger

當下列任一情況成立時，Scrum Master / Orchestrator 應明確觸發 formal review，而不是把 worker completion 視為 sprint-ready：

1. 任務變更了 shared workflow、global skill 行為、routing、authority boundary、或 shared governance asset。
2. 任務改變了何時應該觸發 review / retrospective / QA gate。
3. 任務涉及跨 worker handoff、cross-spec 依賴、或任何可能造成 false-green / overclaim 的高風險面。
4. 任務雖然完成實作，但尚未交付可讀回的 evidence（tests、reports、diff refs、artifact refs）。
5. 任務應有 capability / regression eval evidence，但 `eval-harness` 或等價 EDD 結果缺失、過期、或未被整理進 handoff。

Review ownership:

- Scrum Master / Orchestrator：負責**觸發** review gate 與收斂證據
- Reviewer / QA lane：產生 immediate review signal
- spec-local `review.md`：記錄 formal verdict
- Human：保有高風險邊界變更的最終接受權

EDD / Eval expectation:

- Scrum Master / Orchestrator 在 QC / review gate 應檢查是否存在 `eval-harness` / EDD evidence，特別是 capability eval 與 regression eval。
- 若應有 eval evidence 卻缺失，應視為 review blocker 或至少降級為 `review_pending`，而不是直接推進到 sprint-ready。

### Circuit Breaker

```go
// internal/qaqc/circuit_breaker.go
func (cb *CircuitBreaker) ShouldBreak(ctx context.Context, taskID string) bool {
    failures := cb.getFailureCount(ctx, taskID)
    
    if failures >= cb.threshold {
        // 熔斷：通知 HITL
        cb.notifyHITL(ctx, taskID, fmt.Sprintf("Task failed %d times", failures))
        return true
    }
    
    return false
}
```

---

## Phase 5: Handle Clarification

### 自動解決

```go
// internal/clarification/handler.go
func (h *Handler) AutoResolve(ctx context.Context, question string) (*Answer, error) {
    // 1. 查詢 Knowledge Graph
    kgAnswer := h.kg.Query(ctx, question)
    if kgAnswer.Confidence > 0.8 {
        return kgAnswer, nil
    }
    
    // 2. 查詢 Lesson Learned
    lessons := h.lessonRepo.Search(ctx, question)
    if len(lessons) > 0 {
        return h.synthesizeAnswer(lessons), nil
    }
    
    // 3. 無法自動解決 → HITL
    return nil, ErrNeedHumanInput
}
```

### HITL 升級

```go
// internal/clarification/hitl.go
func (h *HITLHandler) Escalate(ctx context.Context, task *Task, question string) error {
    notification := &HITLNotification{
        TaskID: task.ID,
        Type: "clarification",
        Question: question,
        Priority: h.calculatePriority(task),
        CreatedAt: time.Now(),
    }
    
    return h.notifier.Send(ctx, notification)
}
```

---

## Phase 6: Extract Lessons (Retro)

### 觸發條件

```go
// internal/retro/extractor.go
func (e *Extractor) ShouldTrigger(ctx context.Context, task *Task) bool {
    return task.Iteration > 1 || // 重試任務
           task.Status == StatusFailed || // 失敗任務
           task.HasClarification // 有釐清問題
}
```

### Agentic Retrospective Trigger

除上述 retry / failed / clarification 條件外，若出現下列情況，也應明確觸發 retrospective analysis：

1. 同一類 review rejection reason 重複出現
2. Agents 持續誤解 review trigger / handoff boundary
3. 任務產生 false-green、authority-surface confusion、或 overclaim
4. 重複 blocker 指向 swarm 角色切分不清（human/orchestrator/worker/reviewer）
5. runtime / evidence / traceability friction 在多個 task 或 sprint 反覆發生

Retro output 必須至少分類為：

- spec-local lesson
- issue-log candidate
- shared checklist / template update
- shared prompt / guidance update
- skill change candidate

進一步規則：

- 若問題已有既有 active spec / completed-baseline CR 可承接，優先回掛既有 owner。
- 若暫時找不到既有 owner、但證據尚不足以 justify 新 spec / shared skill change，先停在 issue-log candidate。
- 只有 repeated pattern、穩定 root cause、與明確 promotion threshold 都成立時，才允許升級為 shared process / skill change candidate。

Retrospective ownership:

- Scrum Master / Orchestrator：負責**Raise trigger**
- Human / workflow owner：決定是留在 spec-local 還是提升為 shared process / skill change
- Scrum Master / Orchestrator 不得把 retro 結論直接包裝成新的 authoring authority；它只負責 classification / evidence bundling / handoff。

### 萃取知識

```go
func (e *Extractor) Extract(ctx context.Context, task *Task) (*KnowledgeProposal, error) {
    prompt := fmt.Sprintf(`
Extract lessons learned from this task:

Task: %s
Status: %s
Iterations: %d
Execution Logs:
%s

Output JSON with:
- type: "lesson_learned" | "anti_pattern" | "best_practice"
- title: short title
- description: detailed description
- tags: array of tags
`, task.Title, task.Status, task.Iteration, task.ExecutionLogs)

    response := e.llm.Generate(ctx, prompt)
    return parseKnowledgeProposal(response)
}
```

### 儲存到 Knowledge Graph

```go
func (e *Extractor) SaveToKG(ctx context.Context, proposal *KnowledgeProposal) error {
    return e.kgRepo.Create(ctx, proposal)
}
```

---

## 協調模式

### Event-Driven Webhook

```go
// internal/actions/handler.go
func (h *Handler) HandleDetectBreakdown(w http.ResponseWriter, r *http.Request) {
    // 1. 查詢待拆解的 Epics
    epics := h.epicRepo.FindPendingBreakdown(r.Context())
    
    for _, epic := range epics {
        // 2. 拆解 Epic
        tasks, _ := h.breakdown.BreakdownEpic(r.Context(), epic)
        
        // 3. 建立 DAG
        dag, _ := h.scheduler.BuildDAG(tasks)
        
        // 4. 儲存 Tasks
        h.taskRepo.CreateBatch(r.Context(), tasks)
        
        // 5. 更新 Epic 狀態
        h.epicRepo.UpdateStatus(r.Context(), epic.ID, EpicStatusInProgress)
    }
}

func (h *Handler) HandleDispatchTasks(w http.ResponseWriter, r *http.Request) {
    // 1. 查詢可派發的 Tasks
    tasks := h.scheduler.GetDispatchable(r.Context())
    
    for _, task := range tasks {
        // 2. 推送到 Queue
        h.producer.EnqueueTask(r.Context(), task)
        
        // 3. 更新狀態
        h.taskRepo.UpdateStatus(r.Context(), task.ID, StatusQueued)
    }
}
```

---

## 最佳實踐

1. **Idempotent Operations** — 所有操作冪等
2. **Graceful Degradation** — 優雅降級 (LLM 失敗時使用預設值)
3. **Circuit Breaker** — 防止無限重試
4. **HITL Escalation** — 及時升級到人工
5. **Knowledge Accumulation** — 持續累積知識

---

## 參考

- Design Document: `{.agents, .kiro, or .claude}/specs/scrum-master-coordinator/design.md`
- System Boundary Contracts: `{.agents, .kiro, or .claude}/specs/scrum-master-coordinator/system-boundary-contracts.md`
- Co-Evolution Plan: `{.agents, .kiro, or .claude}/specs/scrum-master-coordinator/co-evolution-plan.md`

> 以上為支援的 agent-root 路徑格式；本專案目前以 `.agents` 為主。若該 spec 不存在，應視為 historical/example reference，而不是當前 workspace 必備 artifact。

---

**版本**: 1.0.0  
**最後更新**: 2026-03-04
