# 需求與設計深度訪談 (Requirement & Design Interview Depth)

本檔是 Phase 1 (Requirements) 與 Phase 2 (Design) 的**深度訪談方法論**。目的：在「先生成草稿、不連續發問」的既有流程上，補上兩種互補的訪談技巧，把需求與設計從「看起來完整」推進到「真正想清楚」。

- **CEO 高階價值視角 (Value Lens)** — 在動手前，先從產品/業務價值的高度挑戰前提，確認「在做對的事」。
- **Grilling 逐題追問紀律 (Grilling Discipline)** — 在草稿之後，沿決策樹逐題追問，把每個分支的隱含假設逼出來，直到形成共識。

> 來源與授權見本檔末「Attribution」。Value Lens 改編自 garrytan/gstack 的 `plan-ceo-review`；Grilling 改編自 mattpocock/skills 的 `grill-me` / `grilling`。兩者皆 MIT License。

---

## 何時使用 (Default-On, Skippable)

- **預設啟動**：每次進入 Requirements 或 Design 階段，預設都跑一輪深度訪談。
- **可隨時跳過**：使用者說「直接生成」「不用問了」「先給草稿」時，立即停止追問，改回 draft-first 快速流程；不要強迫、不要愧疚式重複詢問。
- **與既有流程整合**（不違反 `01-requirements.md` 的「不先問一系列連續問題」）：
  1. **先 1–2 個高層前提問題**（Value Lens，逐一問，不是 barrage）。
  2. **生成初始草稿**（既有行為）。
  3. **針對草稿的具體缺口逐題 grilling**（一次一題）。

「不連續發問」禁止的是「一口氣丟一串問題」；逐題追問（問一題、等回答、再問下一題）正是本方法的核心，兩者不衝突。

---

## 技巧一：CEO 高階價值視角 (Value Lens)

在撰寫需求或定稿設計**之前**，用下列精選視角快速掃描。這些是**思考本能**，不是逐條打勾的 checklist——內化它們，挑出真正有張力的 2–4 個切入點向使用者提問即可。

1. **前提挑戰 (Right Problem?)** — 這是要解的對的問題嗎？換個 framing 是否能得到更簡單或更有影響力的解？
2. **產出 vs 代理指標 (Outcome vs Proxy)** — 真正的使用者/業務結果是什麼？這個需求是達成它的最直接路徑，還是在解一個 proxy 問題？
3. **不做會怎樣 (Do-Nothing Test)** — 若完全不做，會發生什麼？這是真實痛點還是假想需求？（呼應 Ponytail Rung 1）
4. **反演反射 (Inversion)** — 除了「怎麼成功」，也問「什麼會讓它失敗 / 變成下一季的噩夢」？把失敗模式提前講出來。
5. **減法即聚焦 (Focus as Subtraction)** — 最高槓桿的決定常是「**不**做什麼」。哪些 scope 可以砍掉或延後而不傷核心結果？
6. **12 個月理想態 (Dream-State / Temporal Depth)** — 一年後這個系統的理想樣貌是什麼？此需求是朝它移動還是背離？
7. **10x-for-2x 檢查** — 是否存在「多 2x 力氣、好 10x」的版本？（僅在 greenfield / 高價值功能值得，避免過度擴張）
8. **後悔最小化 (Regret Minimization)** — 對重大、不可逆的決策，5 年後回頭看，哪個選擇最不會後悔？

**單向門 vs 雙向門**：先判斷決策的可逆性。雙向門（容易回退）→ 快速決定、別過度糾結；單向門（不可逆、高影響：資料模型、對外契約、安全邊界）→ 放慢、逼出更多資訊再決定。

Value Lens 的產出應落地為 `requirements.md` 的「介紹 / 為何需要存在」與「Repo-side Closure vs External Execution」段落，而不是停留在對話裡。

---

## 技巧二：Grilling 逐題追問紀律 (Grilling Discipline)

草稿（或設計骨架）出來後，沿著**決策樹**逐題追問，直到雙方對每個分支有共識。

**核心規則：**

1. **一次只問一題**，等使用者回答後再問下一題。一次丟多題會讓人困惑、降低回答品質。
2. **沿決策樹一支一支走**，逐一解決決策之間的相依關係（先定上游決策，再問被它影響的下游決策）。
3. **每一題都附上你的建議答案**與簡短理由——不要只丟開放題，讓使用者用「確認/修正」的成本回應。
4. **能從程式碼查到的，就去查，不要問**。先探索 codebase（既有模式、契約、命名、相依），把問題留給「只有使用者知道」的部分：業務意圖、優先序、取捨偏好、外部限制。
5. **沒有問題數量上限**：有些需求三題就清楚，有些要二十題。直到分支收斂為止；但使用者可隨時喊停並接受當前狀態。
6. **relentless 但不 redundant**：持續深掘是對的；重複問同一件事、問低價值問題是 prompt 品質問題，要避免。

**追問要鎖定的高價值缺口**（依需求/設計各有側重）：

- 邊緣情況：空值 / 空集合 / 超長輸入 / 錯誤型別 / 上游失敗時，預期行為是什麼？
- 隱含假設：草稿裡哪些「理所當然」其實未經確認？
- 取捨：當兩個需求衝突時，哪個優先？為什麼？
- 邊界：哪些屬於本 spec、哪些 out-of-scope、哪些是 external execution / blocker？
- 成功標準：怎樣才算「做完且正確」？對應哪個可驗證的 AC / EDD 標準？

### Design 階段的 grilling 重點

Design 的決策樹通常是：架構選型 → 契約邊界 → 元件職責 → 失敗模式 → 可觀測性。逐題確認：

- 為什麼是這個架構/方案，而不是替代方案？（與 `design.md` 的 alternatives 呼應）
- 契約邊界切在哪？誰是 Source of Truth？外部主導時的 Pin/Version 為何？
- 每個新 dependency / 抽象是否通過 Ponytail Rung 2–4？（見 `ponytail-yagni-ladder.md`）
- 每條新資料流的 nil / empty / error 路徑怎麼走？是否進入 FMEA？

---

## 訪談產出的落地 (Recording Outcomes)

追問與挑戰的結論**必須寫回正式 artifact**，否則等於沒發生：

- **確認的需求/決策** → 寫入 `requirements.md`（含 REQ-ID）或 `design.md`（含設計決策與理由）。
- **被砍 / 延後的範圍** → 明確標記 `deferred` 或 `out-of-scope`，並附一行理由（呼應 Ponytail Rung 1 與 Focus as Subtraction）。
- **重大且不可逆的取捨** → 在文件中以一行「決策 + 理由 + 替代方案為何被排除」記錄，方便日後追溯（可選：對應 ADR）。
- **仍未解的問題** → 留在 `NEXT_STEPS.md` 的高階摘要或 `reports/`，不要塞進 RTM / SPECS。

不要新增重複的「訪談逐字稿」檔案；訪談的價值在於它收斂出的需求與決策，而不是過程紀錄。

---

## 停止條件 (Stop Conditions)

符合任一即停止追問、收斂進入下一步：

- 每個決策樹分支都已解決，雙方有共識。
- 使用者明確表示滿意 / 喊停 / 要求直接生成。
- 後續問題都變成低價值或重複（再問不會改變結果）。

---

## 反模式 (Anti-Patterns)

- ❌ 一口氣丟一串問題（barrage）——改為逐題。
- ❌ 只丟開放題、不給建議答案——增加使用者負擔。
- ❌ 問本來能從 codebase 查到的事——先探索再問。
- ❌ 把訪談結論留在對話裡、沒寫回 artifact——等於沒做。
- ❌ 在使用者已喊停後仍持續追問——尊重 skippable。
- ❌ 為了「顯得徹底」而強跑完整 18 條 CEO patterns——本方法刻意只保留精選價值子集。

---

## Attribution

本方法論改編自下列兩個 MIT License 開源專案，在此致謝並標註來源以尊重智慧財產權：

- **Grilling 逐題追問紀律**：改編自 [mattpocock/skills](https://github.com/mattpocock/skills) 的 `grill-me` / `grilling` skill。MIT License, Copyright (c) 2026 Matt Pocock。核心理念：「Interview me relentlessly… Ask the questions one at a time… For each question, provide your recommended answer… If a question can be answered by exploring the codebase, explore the codebase instead.」
- **CEO 高階價值視角**：改編自 [garrytan/gstack](https://github.com/garrytan/gstack) 的 `plan-ceo-review` skill（"Cognitive Patterns — How Great CEOs Think" 與 Premise Challenge / Dream-State Mapping）。MIT License, Copyright (c) 2026 Garry Tan。本檔僅取其精選價值導向子集，未照搬完整 18 條 patterns 或 scope 模式。
