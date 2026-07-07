# Modernization Sequencing

不要先改寫，再祈禱。先建立保護，再切割。

## 建議順序

1. **Inventory**
   - Tables, procs, functions, triggers, jobs, integrations

2. **Characterization Baseline**
   - 為關鍵 procedure 建立 fixture / golden-master / parity baseline

3. **Schema Compatibility Review**
   - Type mapping, collation, identity/sequence, datetime/timezone, null semantics

4. **Extract Orchestration First**
   - 先抽離高層商業流程，再處理底層 SQL 細節

5. **Stabilize Persistence Seams**
   - 建立 repository / query boundary，降低 direct-proc coupling

6. **Redesign Batch / Job Workloads**
   - 把 scheduler-heavy / retry-heavy 工作移到 worker model

7. **Dual-run / Parity Verification**
   - 重要路徑做新舊行為比對，至少做到 smoke-level parity

8. **Cutover + Rollback Thinking**
   - 說明切換單位、觀測點、失敗回退策略

## Slice 原則

- 先從 leaf node 與高價值低耦合模組開始
- 避免一次跨太多 bounded contexts
- 不要先動最難、最深、最外部依賴的 proc chain
