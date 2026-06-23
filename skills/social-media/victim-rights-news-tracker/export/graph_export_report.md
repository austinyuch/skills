# 圖形資料庫匯出報告

**匯出時間**：2026-03-16 18:05:47

## 匯出檔案清單

### 網站視覺化格式
- **Cytoscape.js**: `stakeholders_cytoscape.json`
  - 適用於：互動式網路圖、節點可拖曳、可點擊
  - 使用套件：[Cytoscape.js](https://js.cytoscape.org/)

- **D3.js**: `stakeholders_d3.json`
  - 適用於：力導向圖、動態視覺化
  - 使用套件：[D3.js](https://d3js.org/)

### 專業圖形工具格式
- **GraphML**: `stakeholders.graphml`
  - 適用於：Neo4j、Gephi、Cytoscape Desktop
  - 說明：標準 XML 圖形格式，含完整節點屬性

### 資料分析格式
- **CSV 節點**: `stakeholders_nodes.csv`
- **CSV 關係**: `stakeholders_edges.csv`
  - 適用於：Excel、Pandas、R、其他資料分析工具

### 篩選報告
- **篩選條件**: 類別=public_action
- **符合邊緣數**: 2

## 資料統計

- 總節點數：7
- 總關係數：6
- 總發言數：0

### 節點類型分布
- case: 1
- organization: 1
- party: 2
- person: 3

### 立場分布
- ⭐⭐⭐⭐⭐ (5): 4
- ⭐⭐⭐⭐ (4): 1
- ⭐⭐⭐ (3): 1

### 邊緣類型分布
- ally: 1
- hierarchy: 2
- participate: 2
- propose: 1

