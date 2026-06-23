# Skills 整合工作流程指南

本文件說明如何將 `victim-rights-news-tracker` 和 `social-post-generator` 兩個 skills 整合使用，建立完整的新聞追蹤到社群發布工作流程。

---

## 🔄 整合工作流程概覽

```
┌─────────────────────────────────────────────────────────────────────┐
│                    每日工作流程 (Daily Workflow)                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  08:00  ┌─────────────────┐                                         │
│         │  新聞蒐集        │  victim-rights-news-tracker            │
│         │  (Web Search)   │  → 產生 victim-news-daily-YYYYMMDD.md  │
│         └────────┬────────┘                                         │
│                  │                                                  │
│                  ▼                                                  │
│  09:00  ┌─────────────────┐                                         │
│         │  圖譜更新        │  graph_db.py                          │
│         │  & 立場追蹤      │  → 新增實體與關係到 SQLite            │
│         │                 │  → 更新政黨/人物 ⭐ 立場評級            │
│         └────────┬────────┘                                         │
│                  │                                                  │
│                  ▼                                                  │
│  10:00  ┌─────────────────┐                                         │
│         │  發文生成        │  social-post-generator                │
│         │  (3選項)        │  → 讀取新聞報告                        │
│         │                 │  → 產生 social-posts-YYYYMMDD.md     │
│         └────────┬────────┘                                         │
│                  │                                                  │
│                  ▼                                                  │
│  11:00  ┌─────────────────┐                                         │
│         │  人工審核        │  組織管理者選擇                        │
│         │  & 選擇發布      │  Option A / B / C                     │
│         └────────┬────────┘                                         │
│                  │                                                  │
│                  ▼                                                  │
│  12:00  ┌─────────────────┐                                         │
│         │  社群發布        │  Facebook / Instagram / Threads       │
│         │  & 監測回響      │                                       │
│         └─────────────────┘                                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📋 詳細步驟

### Phase 1: 新聞蒐集與分析 (08:00-09:00)

**使用 Skill**: `victim-rights-news-tracker`

**執行步驟**:
1. 啟動 skill 進行網路新聞蒐集
2. 搜尋主題關鍵字：
   - 受害者家屬權益
   - 被害人訴訟參與權
   - 司法改革修法
   - 小燈泡案、命案家屬
   - 被害人家屬保護協會

3. 產生報告：`victim-news-daily-YYYYMMDD.md`
4. 標記立場評級 (⭐ 1-5星)

**輸出檔案**:
```
skills/victim-rights-news-tracker/
├── reports/
│   └── victim-news-daily-20260313.md    # 新聞報告
├── data/
│   └── victim_rights_graph.db           # SQLite 圖譜資料庫
└── export/
    ├── cytoscape-graph-20260313.json    # 網站視覺化用
    └── stance-report-20260313.md        # 立場分析報告
```

---

### Phase 2: 圖譜更新與關聯分析 (09:00-10:00)

**使用工具**: `graph_db.py` + `export_graph.py`

**執行步驟**:

```bash
# 1. 更新圖譜資料庫
cd skills/victim-rights-news-tracker
cd scripts
python3 graph_db.py --mode add_news --report ../../reports/victim-news-daily-20260313.md

# 2. 更新實體立場評級
python3 graph_db.py --mode update_stance --entity "民進黨團" --rating 4 \
  --evidence "支持被害人權益保障法草案"

# 3. 匯出視覺化檔案 (一鍵匯出所有格式)
python3 export_graph.py
```

**資料庫結構更新**:
```
Entity (45個): 政治人物、政黨、法官、律師、案件、新聞
├── 民進黨團 ⭐⭐⭐⭐ (2026-03-13: 支持修法)
├── 國民黨團 ⭐⭐ (2026-03-13: 需更多討論)
├── 王婉諭 ⭐⭐⭐⭐⭐ (2026-03-13: 持續倡議)
└── ...

Relation (38個): 表態、參與、反對、支持
├── 民進黨團 --[支持]--> 被害人權益保障法
├── 王婉諭 --[參與]--> 立法院聲援活動
└── ...
```

---

### Phase 3: 社群發文生成 (10:00-11:00)

**使用 Skill**: `social-post-generator`

**執行步驟**:

```bash
# 基本使用
cd skills/social-post-generator
python3 scripts/post_generator.py \
  --input ../victim-rights-news-tracker/reports/victim-news-daily-20260313.md

# 指定特定主題
python3 scripts/post_generator.py \
  --input ../victim-rights-news-tracker/reports/victim-news-daily-20260313.md \
  --focus "#小燈泡案"

# 指定平台優化
python3 scripts/post_generator.py \
  --input ../victim-rights-news-tracker/reports/victim-news-daily-20260313.md \
  --platform instagram
```

**輸出檔案**:
```
skills/social-post-generator/
└── posts/
    └── social-posts-20260313.md           # 3個發文選項
        ├── 選項 A: 嚴肅正式風格 (修法/制度面)
        ├── 選項 B: 情感訴求風格 (家屬故事)
        └── 選項 C: 行動呼籲風格 (動員分享)
```

---

### Phase 4: 人工審核與發布 (11:00-12:00)

**執行者**: 組織社群管理員

**決策指南**:

| 情境 | 建議選項 | 理由 |
|------|----------|------|
| 有修法新進展 | **A (嚴肅正式)** | 適合深度討論，展現專業性 |
| 有家屬專訪/故事 | **B (情感訴求)** | 引發共鳴，增加分享率 |
| 需要動員/連署 | **C (行動呼籲)** | 明確CTA，提升參與度 |
| 週間工作日 | **A** | 適合理性閱讀時段 |
| 週末/節日 | **B** | 適合深度閱讀與情感連結 |
| 緊急議題 | **C** | 快速擴散，爭取曝光 |

**審核檢查清單**:
- [ ] 事實查核：引用的數據/日期是否正確
- [ ] 法律檢查：用詞是否符合法律定義
- [ ] 倫理檢查：是否保護家屬隱私
- [ ] 圖片確認：是否有版權/授權
- [ ] Hashtag 適切性：是否與平台趨勢相符

---

## 📊 週期性工作流程

### 每日 (Daily)
- [ ] 新聞追蹤與報告生成
- [ ] 圖譜更新 (如有新聞)
- [ ] 社群發文 (3選1)

### 每週 (Weekly)
- [ ] **週一**: 檢視上週發文成效數據
- [ ] **週三**: 圖譜匯出更新至網站
- [ ] **週五**: 資料庫備份
- [ ] **週日**: 下週主題規劃

```bash
# 週五備份流程
cd skills/victim-rights-news-tracker/scripts
python3 db_maintenance.py --backup

# 匯出所有格式供網站使用
cd skills/victim-rights-news-tracker/scripts
python3 export_graph.py
```

### 每月 (Monthly)
- [ ] **每月1日**: 立場評級全面審核
- [ ] **每月15日**: 標籤系統清理與更新
- [ ] **每月最後一週**: 匯出圖譜至正式 Graph DB (Neo4j)

```bash
# 匯出至 Neo4j
python3 export_graph.py --format neo4j --output monthly-export.cypher
```

---

## 🎯 整合效益

### 1. 資料連貫性
- 新聞 → 圖譜 → 發文，資料流一致
- 標籤系統統一，避免重複或衝突
- 立場評級可追溯，建立公信力

### 2. 效率提升
- 自動化 80% 重複性工作
- 每日只需 1 小時人工審核
- 圖表自動匯出至網站

### 3. 內容品質
- 3 種風格選擇，避免單調
- 立場追蹤建立組織專業形象
- 數據視覺化增強說服力

---

## 🖥️ 網站整合建議

### 圖譜視覺化嵌入

```html
<!-- 使用 Cytoscape.js 匯出檔案 -->
<div id="graph-container"></div>
<script>
fetch('/api/graph-data.json')
  .then(response => response.json())
  .then(data => {
    var cy = cytoscape({
      container: document.getElementById('graph-container'),
      elements: data,
      layout: { name: 'cose', padding: 10 },
      style: [
        { selector: 'node', style: { 'background-color': '#666', 'label': 'data(name)' } },
        { selector: 'edge', style: { 'width': 3, 'line-color': '#ccc' } }
      ]
    });
  });
</script>
```

### 立場追蹤頁面

顯示各政治人物/政黨的 ⭐ 立場評級歷史變化：

```
立場故事線 (Timeline)
├── 2026-03: 監察院報告 ⭐⭐⭐⭐⭐
├── 2026-02: 修法草案提出 ⭐⭐⭐⭐
└── 2026-01: 年度檢討會議 ⭐⭐⭐
```

---

## ⚠️ 重要注意事項

### 1. 隱私保護
- 家屬姓名、照片需經授權
- 案件細節避免過度披露
- 使用代稱保護當事人

### 2. 法律合規
- 發布前事實查核
- 避免誹謗或攻擊性言論
- 引用新聞來源標註清楚

### 3. 資料備份
- 每日自動備份至 `backup/`
- 每月匯出離線存檔
- Git 版本控制 skills 設定

---

## 🆘 常見問題

**Q: 如果當天沒有重要新聞怎麼辦？**
A: 可以使用 `#案件追蹤` 或 `#國際新聞` 標籤回顧過去進展，或生成教育性內容。

**Q: 如何處理敏感案件？**
A: 使用 `--focus` 篩選特定標籤，或手動編輯報告移除敏感內容後再生成發文。

**Q: 圖譜資料會不會變得太大？**
A: SQLite 可處理數百萬筆資料。若超過 10,000 實體，建議遷移至 Neo4j。

**Q: 可以自動發布到社群平台嗎？**
A: 目前需人工審核後手動發布。未來可整合 Facebook/Instagram API 自動化。

---

## 📞 支援與維護

- **Skills 更新**: 每月檢查 `skill-creator` 更新
- **Bug 回報**: 記錄至 `{spec-directory}/reports/issues.md`
- **功能建議**: 使用 `skill-creator` 建立新 skill

---

*最後更新：2026-03-13*  
*整合版本：v1.0*
