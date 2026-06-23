# 圖形資料庫使用指南

本指南詳細說明如何使用受害者家屬權益新聞追蹤器的圖形資料庫功能。

## 概述

圖形資料庫（Graph Database）用於儲存與管理角色（人物、組織、政黨）之間的複雜關係網絡，並支援多種格式匯出供網站視覺化使用。

### 技術架構

- **儲存引擎**：SQLite（輕量級、無需伺服器）
- **資料模型**：節點（Node）+ 邊（Edge）+ 發言時間序列
- **匯出格式**：Cytoscape.js JSON、D3.js JSON、GraphML、CSV

### 適用場景

1. **角色關係追蹤**：記錄 NPO、政黨、政治人物、法界人士的互動
2. **立場視覺化**：在網站呈現互動式立場分布圖
3. **進階分析**：匯入 Neo4j/Gephi 進行社群分析、影響力路徑分析
4. **趨勢研究**：追蹤立場變化歷程、結盟模式演變

---

## 快速開始

### 1. 初始化資料庫

```bash
cd /path/to/victim-rights-news-tracker
python scripts/graph_db.py --init
```

輸出：
```
✅ 資料庫已初始化：data/stakeholders_graph.db
```

### 2. 新增第一個節點

```bash
python scripts/graph_db.py --add-node "wang_wanyu" \
    --name "王婉諭" \
    --type person \
    --role "立法委員" \
    --party "時代力量" \
    --stance 5 \
    --description "小燈泡案受害者母親，積極推動被害人權益保障"
```

輸出：
```
✅ 已新增/更新節點：王婉諭 (wang_wanyu)
```

### 3. 建立關係

```bash
python scripts/graph_db.py --add-edge "wang_wanyu" "victims_rights_assoc" \
    --type ally \
    --interaction "聯合記者會" \
    --date "2024-01-15"
```

輸出：
```
✅ 已新增關係：wang_wanyu --ally--> victims_rights_assoc
```

### 4. 一鍵匯出所有格式

```bash
python scripts/export_graph.py
```

輸出：
```
✅ Cytoscape.js: export/stakeholders_cytoscape.json
✅ D3.js: export/stakeholders_d3.json
✅ GraphML: export/stakeholders.graphml
✅ CSV 節點: export/stakeholders_nodes.csv
✅ CSV 關係: export/stakeholders_edges.csv
```

### 5. 查看統計

```bash
python scripts/graph_db.py --stats
```

輸出：
```
📊 圖形資料庫統計報告

總節點數：12
總關係數：18
總發言數：45
最後更新：2024-01-15 14:30:25

節點類型分布：
  - person: 8
  - organization: 3
  - party: 1

立場分布（已評估）：
  - ⭐⭐⭐⭐⭐ (5): 6
  - ⭐⭐⭐⭐ (4): 2
  - ⭐⭐⭐ (3): 2
```

---

## 詳細操作指南

### 節點管理

#### 節點類型

| 類型 | 說明 | 範例 |
|------|------|------|
| `person` | 個人（政治人物、法官、律師等） | 王婉諭、黃國昌 |
| `organization` | 非營利組織 | 生命權平等協會 |
| `party` | 政黨 | 時代力量、民進黨 |
| `official` | 政府官員 | 法務部長 |
| `case` | 特定案件 | 小燈泡案 |

#### 新增節點

**基本語法**：
```bash
python scripts/graph_db.py --add-node "ID" \
    --name "顯示名稱" \
    --type [person|organization|party|official|case] \
    [--role "職稱"] \
    [--party "所屬組織"] \
    [--stance 0-5] \
    [--description "描述"]
```

**範例**：

```bash
# 新增 NPO 組織
python scripts/graph_db.py --add-node "victims_rights_assoc" \
    --name "生命權平等協會" \
    --type organization \
    --stance 5 \
    --description "專注於被害人權益保障的民間團體"

# 新增政黨
python scripts/graph_db.py --add-node "tpp" \
    --name "時代力量" \
    --type party \
    --stance 5

# 新增法官（暫時不評估立場）
python scripts/graph_db.py --add-node "judge_chen" \
    --name "陳法官" \
    --type person \
    --role "最高法院法官" \
    --stance 0 \
    --description "參與小燈泡案二審審判"
```

#### 更新節點

使用相同的 `--add-node` 指令，系統會自動更新現有節點：

```bash
# 更新立場評分
python scripts/graph_db.py --add-node "judge_chen" \
    --name "陳法官" \
    --type person \
    --stance 4 \
    --description "在研討會發表支持被害人訴訟參與的見解"
```

### 關係管理

#### 關係類型

**基礎類型** (5種):

| 類型 | 說明 | 使用情境 | 顏色 |
|------|------|----------|------|
| `ally` | 同盟 | 聯合聲明、共同活動、提案連署 | 🟢 綠色 |
| `oppose` | 對立 | 公開辯論、反對立場、阻擋修法 | 🔴 紅色 |
| `interact` | 互動 | 一般交流（通用型） | ⚪ 灰色 |
| `hierarchy` | 上下級 | 政黨-黨員、組織-成員 | ⚫ 深灰 |
| `family` | 家屬關係 | 受害者家屬 | 🩷 粉紅 |

**進階類型** (8種 - 新增):

| 類型 | 說明 | 使用情境 | 顏色 | 互動類別 |
|------|------|----------|------|----------|
| `organize` | 主辦 | 發起活動、舉辦記者會 | 🟣 紫色 | public_action |
| `participate` | 參與 | 出席活動、參與會議 | 🔵 藍色 | public_action |
| `support` | 支持 | 聲援、提供協助、聯合倡議 | 🟢 亮綠 | organizational |
| `propose` | 提案 | 提出法案、修法建議 | 🟠 橙色 | legislative |
| `represent` | 代表 | 代表發言、出席會議 | 🔵 淺藍 | media |
| `mention` | 提及 | 媒體報導中提及 | ⚪ 淺灰 | media |
| `funds` | 資金 | 資助、捐款 | 🟠 深橙 | organizational |
| `lobby` | 遊說 | 法案遊說、施壓 | 🩵 青色 | legislative |
| `monitor` | 監督 | 追蹤案件、監督程序 | 🩶 灰色 | social |
| `inquiry` | 質詢 | 正式質詢、調查 | 🩶 灰色 | legal |
| `debate` | 辯論 | 公開辯論、討論 | ⚪ 淺灰 | media |
| `cosign` | 連署 | 法案連署、聯合聲明 | 🟣 紫色 | public_action |
| `coordinate` | 協調 | 跨組織協調、溝通 | 🩵 青色 | organizational |

#### 關係屬性 (新增)

每個關係現在包含以下屬性：

| 屬性 | 類型 | 說明 | 預設值 |
|------|------|------|--------|
| `strength` | float (0.0-1.0) | 關係強度 | 0.5 |
| `direction` | string | 方向性 (directed/undirected/bidirectional) | undirected |
| `verified` | boolean | 是否已驗證 | false |
| `evidence_count` | integer | 證據數量 | 1 |
| `first_seen` | date | 首次觀察日期 | 同 date |
| `sentiment` | float (-1.0 to 1.0) | 情感傾向 | null |
| `interaction_category` | string | 互動類別 | auto-detected |

**互動類別 (Interaction Categories)**:

| 類別 | 說明 | 包含的邊緣類型 |
|------|------|----------------|
| `public_action` | 公開行動 | organize, participate, cosign |
| `legislative` | 立法活動 | propose, lobby, inquiry |
| `media` | 媒體活動 | represent, mention, debate |
| `legal` | 法律程序 | inquiry |
| `organizational` | 組織運作 | support, funds, coordinate |
| `social` | 社會監督 | monitor |
| `general` | 一般互動 | ally, oppose, interact, hierarchy |

#### 建立關係 (基礎)

**基本語法**：
```bash
python scripts/graph_db.py --add-edge "來源ID" "目標ID" \
    --type [ally|oppose|interact|hierarchy] \
    [--interaction "互動類型"] \
    [--date "YYYY-MM-DD"] \
    [--description "描述"]
```

**範例**：

```bash
# 同盟關係 - 聯合記者會
python scripts/graph_db.py --add-edge "wang_wanyu" "victims_rights_assoc" \
    --type ally \
    --interaction "聯合記者會" \
    --date "2024-01-15" \
    --description "共同呼籲加速修法"

# 質詢互動
python scripts/graph_db.py --add-edge "wang_wanyu" "minister_of_justice" \
    --type interact \
    --interaction "立法院質詢" \
    --date "2024-01-10" \
    --description "質詢被害人保護法修法進度"

# 上下級關係
python scripts/graph_db.py --add-edge "wang_wanyu" "tpp" \
    --type hierarchy \
    --interaction "黨籍隸屬"
```

### 發言記錄管理

#### 記錄發言

**基本語法**：
```bash
python scripts/graph_db.py --add-statement "節點ID" \
    --date "YYYY-MM-DD" \
    --occasion "發言場合" \
    --content "發言內容摘要" \
    [--stance-mark 1-5] \
    [--source-url "URL"] \
    [--source-media "媒體名稱"]
```

**範例**：

```bash
python scripts/graph_db.py --add-statement "wang_wanyu" \
    --date "2024-01-15" \
    --occasion "立法院司法法制委員會質詢" \
    --content "法務部至今未提出具體修法時間表，令人失望。被害人家屬已經等了太久。" \
    --stance-mark 5 \
    --source-url "https://www.ly.gov.tw/..." \
    --source-media "立法院公報"
```

#### 查詢發言歷史

目前需透過程式碼查詢（未來版本將加入 CLI 查詢功能）：

```python
from scripts.graph_db import GraphDatabase

db = GraphDatabase()
statements = db.get_node_statements("wang_wanyu", limit=10)

for stmt in statements:
    print(f"{stmt['date']} - {stmt['occasion']}")
    print(f"  {stmt['content'][:50]}...")
    print(f"  立場：{'⭐' * stmt['stance_mark']}")
```

### 網絡查詢

#### 查詢個人網絡

查看某角色周邊的人物網絡：

```bash
python scripts/graph_db.py --query-network "wang_wanyu" --depth 2
```

輸出範例：
```
🌐 人物網絡查詢結果（中心：wang_wanyu，深度：2）

節點數量：8
關係數量：12

人物清單：
  - 王婉諭 (person) ⭐⭐⭐⭐⭐
  - 生命權平等協會 (organization) ⭐⭐⭐⭐⭐
  - 時代力量 (party) ⭐⭐⭐⭐⭐
  - 黃國昌 (person) ⭐⭐⭐⭐
  - 民間司法改革基金會 (organization) ⭐⭐⭐⭐⭐

關係清單：
  - wang_wanyu --[ally]--> victims_rights_assoc
  - wang_wanyu --[hierarchy]--> tpp
  - wang_wanyu --[ally]--> kc_huang
```

---

## 資料匯出

### 匯出格式對照

| 格式 | 檔案 | 適用場景 | 特色 |
|------|------|----------|------|
| **Cytoscape.js** | `stakeholders_cytoscape.json` | 網站前端 | 互動式、可拖曳、完整屬性 |
| **D3.js** | `stakeholders_d3.json` | 網站前端 | 力導向動畫、高度自定義 |
| **GraphML** | `stakeholders.graphml` | 專業工具 | 通用格式、Neo4j/Gephi 支援 |
| **CSV** | `stakeholders_nodes/edges.csv` | 資料分析 | Excel 友善、表格形式 |

### 單一格式匯出

```bash
# Cytoscape.js 格式（網站互動圖）
python scripts/graph_db.py --export --format cytoscape --output network.json

# D3.js 格式（力導向圖）
python scripts/graph_db.py --export --format d3 --output network_d3.json

# GraphML 格式（專業工具）
python scripts/graph_db.py --export --format graphml --output network.graphml

# CSV 格式（Excel 分析）
python scripts/graph_db.py --export --format csv --output network
# 產生：network_nodes.csv + network_edges.csv
```

### 批次匯出（推薦）

```bash
python scripts/export_graph.py
```

這會同時產生所有格式至 `export/` 目錄。

---

## 網站整合

### Cytoscape.js 整合範例

#### 基礎嵌入

```html
<!DOCTYPE html>
<html>
<head>
    <script src="https://unpkg.com/cytoscape@3.26.0/dist/cytoscape.min.js"></script>
    <style>
        #cy { width: 100%; height: 600px; background: #f8f9fa; }
    </style>
</head>
<body>
    <div id="cy"></div>
    <script>
        fetch('stakeholders_cytoscape.json')
            .then(r => r.json())
            .then(data => {
                cytoscape({
                    container: document.getElementById('cy'),
                    elements: data,
                    style: [
                        { selector: 'node', style: { 'label': 'data(label)' } },
                        { selector: 'edge', style: { 'label': 'data(label)' } }
                    ],
                    layout: { name: 'cose', padding: 10 }
                });
            });
    </script>
</body>
</html>
```

#### 進階版本（含互動）

參考 [references/output-templates.md](references/output-templates.md) 的「網站視覺化範本」章節，包含：
- 立場顏色圖例
- 節點點擊顯示詳情
- 搜尋與篩選功能
- 響應式布局

### D3.js 整合範例

```html
<script src="https://d3js.org/d3.v7.min.js"></script>
<script>
fetch('stakeholders_d3.json')
    .then(r => r.json())
    .then(data => {
        const svg = d3.select('svg');
        const simulation = d3.forceSimulation(data.nodes)
            .force('link', d3.forceLink(data.links).id(d => d.id))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(width/2, height/2));
        
        // 繪製連線與節點...
    });
</script>
```

完整範例見 [references/output-templates.md](references/output-templates.md)。

---

## 遷移至正式 Graph DB

### 匯入 Neo4j

#### 方法 1：使用 CSV 匯入

```bash
# 將 CSV 檔案放入 Neo4j import 目錄
cp export/stakeholders_nodes.csv /var/lib/neo4j/import/
cp export/stakeholders_edges.csv /var/lib/neo4j/import/

# 使用 Neo4j Browser 執行 Cypher 查詢
```

```cypher
// 匯入節點
LOAD CSV WITH HEADERS FROM 'file:///stakeholders_nodes.csv' AS row
CREATE (n:Stakeholder {
    id: row.id,
    name: row.name,
    type: row.type,
    stance: toInteger(row.stance)
});

// 匯入關係
LOAD CSV WITH HEADERS FROM 'file:///stakeholders_edges.csv' AS row
MATCH (a:Stakeholder {id: row.source}), (b:Stakeholder {id: row.target})
CREATE (a)-[:RELATIONSHIP {type: row.type}]->(b);
```

#### 方法 2：使用 GraphML 匯入

```bash
# 使用 Gremlin 或 APOC 插件
CALL apoc.import.graphml('file:///stakeholders.graphml', {})
```

### 進階查詢範例

```cypher
// 查詢所有強烈支持者的同盟關係
MATCH (n:Stakeholder)-[r:RELATIONSHIP {type: 'ally'}]->(m:Stakeholder)
WHERE n.stance = 5 AND m.stance = 5
RETURN n.name, m.name, r.interaction;

// 查詢某人的網絡（深度2）
MATCH path = (center:Stakeholder {id: 'wang_wanyu'})-[:RELATIONSHIP*1..2]-(n)
RETURN center, n, relationships(path);

// 社群偵測（使用 Louvain 算法）
CALL gds.louvain.stream('myGraph')
YIELD nodeId, communityId
RETURN gds.util.asNode(nodeId).name AS name, communityId
ORDER BY communityId;
```

---

## 最佳實踐

### 命名規範

**節點 ID**：
- 使用英文小寫 + 底線
- 格式：`[姓氏]_[名字]` 或 `組織英文名`
- 範例：`wang_wanyu`, `huang_kuo_chang`, `victims_rights_assoc`

**中文名稱**：
- 使用完整正式名稱
- 範例：「王婉諭」、「生命權平等協會」

### 資料維護

**定期備份**：
```bash
# 每日備份
cp data/stakeholders_graph.db backup/stakeholders_$(date +%Y%m%d).db
```

**版本控制**：
- 不要將 `.db` 檔案提交至 Git（已加入 `.gitignore`）
- 定期匯出 CSV 作為可讀取的備份

**資料清理**：
```bash
# 檢查孤立節點（無任何關係的節點）
python scripts/graph_db.py --stats

# 檢查重複關係（未來版本將加入）
```

### 效能建議

**小型網絡（<100 節點）**：
- SQLite 完全足夠
- 所有功能可正常使用

**中型網絡（100-1000 節點）**：
- 建議定期匯出至 Neo4j 進行進階分析
- Cytoscape.js 網頁可能需要 WebGL 加速

**大型網絡（>1000 節點）**：
- 考慮完全遷移至 Neo4j
- 使用分層視覺化（先顯示核心節點）

---

## 故障排除

### 常見問題

**Q1: 新增關係時顯示「Source/Target node does not exist」**

A: 請先確保兩端節點都已建立：
```bash
python scripts/graph_db.py --add-node "source_id" --name "名稱" --type person
python scripts/graph_db.py --add-node "target_id" --name "名稱" --type organization
# 然後再建立關係
```

**Q2: 匯出檔案為空或格式錯誤**

A: 檢查資料庫是否有資料：
```bash
python scripts/graph_db.py --stats
```

**Q3: Cytoscape.js 網頁無法載入**

A: 檢查：
1. `stakeholders_cytoscape.json` 是否存在於同一目錄
2. 瀏覽器主控台是否有 CORS 錯誤（本地測試時使用本地伺服器）

**Q4: 如何刪除錯誤的節點或關係？**

A: 目前需直接操作 SQLite：
```bash
sqlite3 data/stakeholders_graph.db "DELETE FROM nodes WHERE id = '錯誤ID';"
```

（未來版本將加入 `--delete` 功能）

---

## 進階功能（v2.0 新增）

### 關係強度計算

自動計算所有關係的強度值：

```bash
python scripts/export_graph.py --calculate-strength
```

**計算邏輯**：
- 基礎強度：0.5
- 證據加成：每個證據 +0.1（上限 +0.3）
- 時間加成：30 天內的互動 +0.1
- 時間衰減：超過 365 天每天 -0.0005

### 篩選匯出

只匯出符合特定條件的關係：

```bash
# 只匯出強度 ≥ 0.7 的關係
python scripts/export_graph.py --min-strength 0.7

# 只匯出已驗證的關係
python scripts/export_graph.py --verified-only

# 只匯出特定互動類別
python scripts/export_graph.py --category public_action

# 組合篩選條件
python scripts/export_graph.py --calculate-strength --min-strength 0.6 --verified-only
```

### 網絡分析報告

產生完整的網絡分析報告：

```bash
python scripts/analyze_network.py
```

報告內容包括：
- 網絡指標（密度、平均連接數、驗證比例）
- 關鍵行為者識別（Degree Centrality Top 5）
- 關係強度分布
- 互動類別分析
- Mermaid 網絡圖
- 洞察與建議

### 資料庫遷移

更新現有資料的邊緣類型與屬性：

```bash
python scripts/migrate_graph_db.py
```

此腳本會：
1. 檢查並新增必要的資料表欄位
2. 將舊的 "interact" 邊緣自動分類為具體類型
3. 建立新索引以提升查詢效能
4. 顯示遷移統計報告

---

## 版本歷史

- **v2.0** (2024-03-16)：增強版本
  - 新增 8 種進階邊緣類型
  - 新增 7 個邊緣屬性（strength, direction, verified 等）
  - 自動關係強度計算
  - 篩選匯出功能
  - 網絡分析報告產生器
  - 互動類別自動分類
  
- **v1.0** (2024-01-15)：初始版本
  - SQLite 圖形資料庫
  - 支援 4 種匯出格式
  - Cytoscape.js 與 D3.js 網站範本

---

## 參考資源

- [SKILL.md](../SKILL.md) - 技能主文件
- [output-templates.md](output-templates.md) - 網站視覺化範本
- [Cytoscape.js 文件](https://js.cytoscape.org/)
- [D3.js 文件](https://d3js.org/)
- [Neo4j 文件](https://neo4j.com/docs/)
