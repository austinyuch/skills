# Ponytail Minimal Implementation Ladder (YAGNI Operationalization)

> Adapted from [ponytail](https://github.com/DietrichGebert/ponytail) by DietrichGebert, MIT License.  
> Original tagline: "Makes your AI agent think like the laziest senior dev in the room. The best code is the code you never wrote."

## 核心原則

在新增任何程式碼、元件、依賴或抽象之前，必須依序走完以下六級階梯（ladder），並在設計或實作文件中**展示思考過程**（show your work），而非僅給出結論。

> **Lazy, not negligent**：trust-boundary validation、data-loss handling、security、accessibility 永遠不在精簡範圍內。精簡的是不必要的功能與過度設計，不是安全與正確性。

---

## The 6-Rung Ladder

```
1. Does this need to exist?   → no: skip it (YAGNI)
2. Stdlib does it?            → use it
3. Native platform feature?   → use it
4. Installed dependency?      → use it
5. One line?                  → one line
6. Only then: the minimum that works
```

### Rung 1: Does this need to exist? (YAGNI Gate)

- 這個功能、模組、API endpoint、資料表、或設定項目，是否真的有已確認的需求支撐？
- 是否只是「以後可能會用到」或「看起來應該要有」？
- 若答案為 no，**直接跳過**，不在 requirements.md、design.md 或 tasks.md 中規劃。
- 與 SDD Phase 1 的銜接：這是需求階段的第一道過濾閘門。在撰寫 `requirements.md` 前，先自問：這個需求本身是否需要存在？

### Rung 2: Stdlib does it?

- 當前語言或 runtime 的**標準函式庫**是否已經提供此功能？
- 標準函式庫指該語言或平台內建、無需額外安裝即可使用的函式與模組。
- 若標準函式庫已涵蓋，**使用標準函式庫**，不引入額外包裝或 polyfill。
- 不同技術堆疊的標準函式庫範圍不同；agent 應根據當前專案使用的語言與 runtime 判定。

### Rung 3: Native platform feature?

- 當前**執行平台**（作業系統、runtime、嵌入式環境、或框架）是否提供原生能力？
- 原生能力指平台本身內建、不需要額外 library 或 wrapper 即可直接使用的功能。
- 若原生平台已支援，**使用原生能力**，不疊加抽象層。
- 平台定義依當前專案而異：可能是 OS syscall、runtime API、嵌入式硬體暫存器、或框架內建 component。agent 應根據實際 target platform 判定。

### Rung 4: Installed dependency?

- 專案**現有依賴清單**（`package.json`、`go.mod`、`requirements.txt`、`Cargo.toml` 等）中，是否已有可解決此問題的套件或 library？
- 若現有依賴已涵蓋，**使用現有依賴**，不增加新 dependency。
- 新增 dependency 會增加建構時間、授權審查成本、安全表面積與維護負擔；應在用完既有工具後才考慮。

### Rung 5: One line?

- 若必須寫新程式碼，能否在**極短片段**（一行或數行）內完成？
- 簡單的資料轉換、條件賦值、或格式調整，不需要包成完整的 class / module / service / microservice。
- 若可以極短片段解決，**就寫極短片段**，不包裝成過度抽象的結構。
- 注意：「一行」是概念性表達，不是嚴格的行數限制；重點在於避免為了 trivial 邏輯創建不必要的抽象層。

### Rung 6: Only then — the minimum that works

- 走完 rung 1-5 後，若確實需要新增程式碼，只寫「能工作的最小實作」。
- 不是「未來可能擴展的版本」，不是「預留接口的通用版本」，而是**當下需求所需的最小正確實作**。
- 與 KISS 原則一致：複雜度是技術債的主要來源。

---

## 與 SDD 各階段的整合

### Phase 1: Requirements (Rung 1 為主)

- 在撰寫 `requirements.md` 前，先對每個需求執行 **Rung 1**：這個需求是否真的需要存在？
- 若只是 speculative 功能，應在 requirements 階段就標記為 `deferred` 或 `out-of-scope`，不進入 design。
- 展示方式：在 `requirements.md` 的「介紹」或「需求」段落，簡短說明為何這些需求是必要的（例如引用 stakeholder request、bug report、或業務指標）。

### Phase 2: Design (Rung 2-4 為主)

- 在技術選型、架構設計、或決定引入新 dependency / 新元件時，必須展示 ladder rung 2-4 的思考。
- 展示方式：在 `design.md` 的「架構」或「技術選型」段落，對每個新引入的依賴或元件，回答：
  - 標準函式庫是否已涵蓋？
  - 原生平台是否已支援？
  - 現有依賴是否已涵蓋？
- 若必須引入新 dependency，應在 design 中明確說明「為何 rung 2-4 無法滿足」，並記錄選型理由。

### Phase 4: Implementation (Rung 5-6 為主)

- 在實作每個任務前，必須展示 ladder rung 5-6 的思考。
- 展示方式：在「思考過程展示」的「方案選擇依據」中，回答：
  - 這個任務能否用更少的程式碼完成？
  - 是否過度包裝了一個本來可以一行解決的邏輯？
  - 實作是否為「最小可用」，而非「預留擴展」？
- 與 TDD 的關係：先寫測試，再寫最小通過實作，再重構。重構時可用 ladder 檢視是否仍有過度設計。

---

## 與 Code-Review Skill 的協作

Ponytail ladder 是**設計與實作階段的前置思考框架**；`code-review` skill 家族是**複核階段的 left-shift 偵測工具**。兩者協作方式如下：

### 職責分界

| 階段 | Ponytail Ladder | Code-Review Skill 家族 |
|---|---|---|
| Phase 2 Design | 在選型時防止 over-engineering | `code-review --graph-only` 佐證 blast-radius |
| Phase 4 Implementation | 在實作時防止 over-building | `code-refactoring-advisor` 偵測 god-file / long-method；`test-quality-reviewer` 確認測試不過度 |
| Phase 5 Review | 不直接參與 | `code-review` 審查 diff；`security-risk-reviewer` 確保精簡沒有犧牲安全 |

### 實務協作模式

1. **Phase 4 的 TDD REFACTOR 步驟**：
   - 先以 ladder 自我檢視：這段程式碼是否可以用更少行數完成？
   - 再執行 `code-refactoring-advisor`：是否有 Fowler smell（long method、god file、duplicated blocks）？
   - 兩者結果若衝突（ladder 說「一行就夠」，refactoring advisor 說「抽出 function」），以「可讀性與可測試性」為最終判準，而非單純行數最少。

2. **Phase 5 Review 的過度設計偵測**：
   - `code-review` 的 diff review 應檢查：新引入的 dependency 是否有 ladder rung 2-4 的紀錄？
   - `test-quality-reviewer` 應檢查：測試是否過度複雜（例如為了一個標準函式庫的內建函數寫了過多 test helper）？
   - 若發現未經 ladder 思考就引入的新 dependency 或新抽象，review 應標記為 `over-engineering risk`，並要求補上 ladder 紀錄。

3. **與 `security-risk-reviewer` 的關係**：
   - ladder 的精簡**不包括**安全檢查的省略。
   - 若 `security-risk-reviewer` 發現因「最小化」而遺漏的輸入驗證、TLS 驗證、或錯誤處理，這不是 ladder 的合理結果，而是 implementation 錯誤。

---

## 展示格式範例

### Phase 1 Example (Rung 1)

```markdown
### 需求 1 [REQ-FEAT-001]

**用戶故事：** 作為使用者，我希望匯出報表，以便離線查看。

#### 技術選型思考 (Ponytail Ladder)

- Rung 1: 報表匯出是已確認的核心功能，來自客戶訪談記錄 #42。✅ 需要存在。
```

### Phase 2 Example (Rung 2-4)

```markdown
### 技術選型：資料序列化格式

- Rung 2 (Stdlib): 當前語言的標準函式庫已提供 JSON / CSV 序列化能力，無需額外套件。
- Rung 3 (Native): N/A（此為 pure data transformation）。
- Rung 4 (Installed): 無現有資料格式 library。
- **結論**：使用標準函式庫內建的序列化功能，不引入額外 dependency。
```

### Phase 4 Example (Rung 5-6)

```markdown
### 思考過程展示

1. **問題分析**：需要將內部資料結構轉為匯出格式。
2. **方案選擇依據**：
   - Rung 5: 標準函式庫的序列化函數可直接使用，無需包裝成 `Exporter` class。
   - Rung 6: 最小實作為 inline call，搭配現有的 validation pipe。
3. **規範與契約依據**：參考 `contract/export.yaml` 的 `format` field 定義。
4. **需求追溯**：此任務對應 REQ-FEAT-001。
```

---

## License Note

本 reference 改編自 DietrichGebert/ponytail (MIT License)。原始專案的完整內容與 benchmark 請參閱：
- GitHub: https://github.com/DietrichGebert/ponytail
- License: https://github.com/DietrichGebert/ponytail/blob/main/LICENSE
