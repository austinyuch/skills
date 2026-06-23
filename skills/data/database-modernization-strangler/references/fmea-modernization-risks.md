# FMEA Modernization Risks

對高風險 modernization 判斷，必須加上一個輕量 FMEA / risk register。

## 最小欄位

| Field | Meaning |
|---|---|
| Failure Mode | 可能失敗模式 |
| Cause | 造成原因 |
| Effect | 影響 |
| Detection | 如何發現 |
| Severity | high / medium / low |
| Likelihood | high / medium / low |
| Mitigation | 緩解手段 |
| Next Evidence Needed | 還缺什麼證據 |

## 常見 Failure Modes

- name-only classification 被誤當成已驗證決策
- hidden trigger / job side effects 未盤點
- transaction boundary 誤判
- dynamic SQL / permissions drift 導致重寫後權限行為改變
- batch / settlement 路徑沒有 reconciliation 策略
- rollback 只回退 code path，無法回退 data state
- dual-run 期間 source of truth 不清

## 使用規則

- 不要求精密分數
- 但至少要讓風險、成因、偵測方式與下一步證據透明化
