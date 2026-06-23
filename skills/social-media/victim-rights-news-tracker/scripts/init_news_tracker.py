#!/usr/bin/env python3
"""
Victim Rights News Tracker - Initialization Script
第一次初始化與新聞資料收集
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# 設定專案路徑
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
REPORTS_DIR = DATA_DIR / "reports"
LOGS_DIR = PROJECT_ROOT / "logs"
CONFIG_FILE = PROJECT_ROOT / "config" / "init_config.json"


class NewsTrackerInitializer:
    """新聞追蹤系統初始化器"""

    def __init__(self):
        self.config = self._load_or_create_config()
        self.setup_directories()

    def _load_or_create_config(self):
        """載入或創建設定檔"""
        config_path = PROJECT_ROOT / "config"
        config_path.mkdir(exist_ok=True)

        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)

        # 預設設定
        default_config = {
            "initialized_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "search_keywords": {
                "group_a_victim_rights": [
                    "受害者家屬 權益 台灣",
                    "被害者家屬 人權 新聞",
                    "victim family rights Taiwan",
                ],
                "group_b_judicial_injustice": [
                    "司法不公 加害者 受害者家屬",
                    "司法改革 被害人保護",
                    "judicial injustice victim family Taiwan",
                ],
                "group_c_human_rights_activities": [
                    "生命權平等協會 活動",
                    "被害人保護協會 新聞",
                    "victim advocacy group Taiwan",
                ],
                "group_d_legislation": [
                    "刑事被害人保護法 修法",
                    "司法改革 被害人訴訟參與",
                    "被害人權益 法案",
                    "犯罪被害人保護法 修正案",
                ],
            },
            "target_np_os": [
                "生命權平等協會",
                "被害人保護協會",
                "犯罪被害人保護協會",
                "司法改革基金會",
            ],
            "target_persons": ["王婉諭", "林志潔", "黃國昌"],
            "entity_resolution": {
                "require_unique_id": True,
                "track_aliases": True,
                "stance_tracking_enabled": True,
            },
            "data_sources": {
                "web_search": {
                    "enabled": True,
                    "last_update": None,
                    "update_frequency": "daily",
                },
                "news_feeds": {
                    "enabled": True,
                    "sources": ["中央社", "聯合報", "自由時報", "中國時報"],
                },
            },
            "stance_assessment": {
                "scale": "5_star",
                "criteria": {
                    "5_star": "強烈支持被害人權益",
                    "4_star": "支持被害人權益",
                    "3_star": "中立或平衡觀點",
                    "2_star": "消極或迴避",
                    "1_star": "反對或阻礙",
                },
            },
            "first_collection": {
                "date_range": {"start": "2024-01-01", "end": "2024-12-31"},
                "status": "pending",
            },
        }

        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)

        return default_config

    def setup_directories(self):
        """設定目錄結構"""
        directories = [
            DATA_DIR / "raw" / "news",
            DATA_DIR / "raw" / "search_results",
            DATA_DIR / "processed" / "entities",
            DATA_DIR / "processed" / "stances",
            DATA_DIR / "processed" / "graph",
            DATA_DIR / "reports" / "daily",
            DATA_DIR / "reports" / "monthly",
            DATA_DIR / "reports" / "entities",
            PROJECT_ROOT / "logs",
            PROJECT_ROOT / "export",
            PROJECT_ROOT / "backup",
            PROJECT_ROOT / "temp",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"✅ 目錄已建立: {directory}")

    def run_first_collection(self):
        """執行第一次新聞資料收集"""
        print("\n" + "=" * 60)
        print("📰 Victim Rights News Tracker - 第一次新聞收集")
        print("=" * 60 + "\n")

        # 1. 建立搜尋模板
        print("📦 Phase 1: 建立搜尋模板...")
        self._create_search_templates()

        # 2. 初始化實體資料庫
        print("\n📦 Phase 2: 初始化實體資料庫...")
        self._init_entity_database()

        # 3. 建立立場追蹤系統
        print("\n📦 Phase 3: 建立立場追蹤系統...")
        self._init_stance_tracking()

        # 4. 建立圖形資料庫
        print("\n🔗 Phase 4: 建立關係圖形資料庫...")
        self._init_graph_database()

        # 5. 產生初始化報告
        print("\n📊 Phase 5: 產生初始化報告...")
        self._generate_init_report()

        # 更新設定檔
        self.config["first_collection"]["status"] = "completed"
        self.config["first_collection"]["completed_at"] = datetime.now().isoformat()

        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

        print("\n" + "=" * 60)
        print("✅ 初始化完成！")
        print("=" * 60)
        print(f"\n📁 資料目錄: {DATA_DIR}")
        print(f"📊 報告目錄: {REPORTS_DIR}")
        print(f"⚙️  設定檔: {CONFIG_FILE}")
        print("\n💡 接下來您可以：")
        print("   1. 查看 reports/init_report.md 了解系統設定")
        print("   2. 執行每日新聞搜尋（使用 websearch 工具）")
        print("   3. 使用 scripts/graph_db.py 管理人物關係")

    def _create_search_templates(self):
        """建立搜尋模板"""
        try:
            template_file = RAW_DIR / "search_templates.json"

            templates = {
                "created_at": datetime.now().isoformat(),
                "keyword_groups": self.config["search_keywords"],
                "search_strategy": {
                    "frequency": "daily",
                    "time_range": "past_24_hours",
                    "sources": ["news", "official"],
                    "language": "zh-TW",
                },
                "output_format": {
                    "include_metadata": True,
                    "include_tags": True,
                    "include_stance": True,
                },
            }

            with open(template_file, "w", encoding="utf-8") as f:
                json.dump(templates, f, ensure_ascii=False, indent=2)

            print(f"   ✅ 搜尋模板建立: {template_file}")
            print(f"   📌 關鍵字群組: {len(self.config['search_keywords'])} 組")

        except Exception as e:
            print(f"   ❌ 搜尋模板建立失敗: {e}")

    def _init_entity_database(self):
        """初始化實體資料庫"""
        try:
            entity_file = PROCESSED_DIR / "entities" / "entity_registry.json"

            # 預設實體
            default_entities = {
                "persons": [
                    {
                        "id": "wang_wanyu",
                        "name": "王婉諭",
                        "type": "person",
                        "role": "立法委員",
                        "organization": "時代力量",
                        "stance": 5,
                        "notes": "小燈泡案受害者母親",
                    }
                ],
                "organizations": [
                    {
                        "id": "victims_rights_assoc",
                        "name": "生命權平等協會",
                        "type": "npo",
                        "focus": "被害人權益",
                        "stance": 5,
                    },
                    {
                        "id": "victim_protection_assoc",
                        "name": "犯罪被害人保護協會",
                        "type": "npo",
                        "focus": "被害人保護",
                        "stance": 4,
                    },
                ],
                "political_parties": [
                    {"id": "dpp", "name": "民主進步黨", "type": "party"},
                    {"id": "kmt", "name": "中國國民黨", "type": "party"},
                ],
            }

            with open(entity_file, "w", encoding="utf-8") as f:
                json.dump(default_entities, f, ensure_ascii=False, indent=2)

            print(f"   ✅ 實體資料庫初始化: {entity_file}")
            print(f"   📊 預設實體: {len(default_entities)} 類型")

        except Exception as e:
            print(f"   ❌ 實體資料庫初始化失敗: {e}")

    def _init_stance_tracking(self):
        """初始化立場追蹤系統"""
        try:
            stance_file = PROCESSED_DIR / "stances" / "stance_registry.json"

            stance_system = {
                "created_at": datetime.now().isoformat(),
                "assessment_scale": "5_star",
                "criteria": self.config["stance_assessment"]["criteria"],
                "tracked_entities": [],
                "stance_history": [],
                "assessment_guidelines": {
                    "5_star": "積極推動修法、多次為家屬發聲、實質行動",
                    "4_star": "公開表態支持、參與相關活動",
                    "3_star": "表示關注但未明確表態，或提出平衡觀點",
                    "2_star": "態度模糊、迴避表態、僅官方客套話",
                    "1_star": "明確反對家屬訴求、阻撓法案進度",
                },
            }

            with open(stance_file, "w", encoding="utf-8") as f:
                json.dump(stance_system, f, ensure_ascii=False, indent=2)

            print(f"   ✅ 立場追蹤系統建立: {stance_file}")
            print(f"   ⭐ 立場評級: 5星級系統")

        except Exception as e:
            print(f"   ❌ 立場追蹤系統建立失敗: {e}")

    def _init_graph_database(self):
        """初始化圖形資料庫"""
        try:
            graph_file = PROCESSED_DIR / "graph" / "graph_db_template.json"

            graph_template = {
                "created_at": datetime.now().isoformat(),
                "database_type": "sqlite",
                "nodes": {
                    "types": ["person", "organization", "party", "official", "case"],
                    "properties": {
                        "person": ["name", "role", "organization", "stance"],
                        "organization": ["name", "type", "focus", "stance"],
                    },
                },
                "edges": {
                    "types": ["ally", "oppose", "interact", "member_of", "supports"],
                    "properties": ["date", "context", "source_url"],
                },
                "example_queries": [
                    "查詢所有立場⭐⭐⭐⭐⭐的人物",
                    "查詢某組織的所有盟友",
                    "查詢人物關係網絡（2度以內）",
                ],
            }

            with open(graph_file, "w", encoding="utf-8") as f:
                json.dump(graph_template, f, ensure_ascii=False, indent=2)

            print(f"   ✅ 圖形資料庫模板: {graph_file}")
            print(f"   📊 節點類型: {len(graph_template['nodes']['types'])}")
            print(f"   🔗 關係類型: {len(graph_template['edges']['types'])}")

        except Exception as e:
            print(f"   ❌ 圖形資料庫初始化失敗: {e}")

    def _generate_init_report(self):
        """產生初始化報告"""
        report_file = REPORTS_DIR / f"init_report_{datetime.now():%Y%m%d}.md"

        keyword_summary = "\n".join(
            [
                f"**{group}**: {', '.join(keywords[:3])}..."
                for group, keywords in self.config["search_keywords"].items()
            ]
        )

        report_content = f"""# Victim Rights News Tracker 初始化報告

**初始化日期**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 系統設定

### 追蹤目標

#### 關注 NPO 組織
{chr(10).join(f"- {npo}" for npo in self.config["target_np_os"])}

#### 關注人物
{chr(10).join(f"- {person}" for person in self.config["target_persons"])}

### 搜尋關鍵字群組

{keyword_summary}

### 立場評估系統

**評級標準**：
- ⭐⭐⭐⭐⭐ (5星): {self.config["stance_assessment"]["criteria"]["5_star"]}
- ⭐⭐⭐⭐ (4星): {self.config["stance_assessment"]["criteria"]["4_star"]}
- ⭐⭐⭐ (3星): {self.config["stance_assessment"]["criteria"]["3_star"]}
- ⭐⭐ (2星): {self.config["stance_assessment"]["criteria"]["2_star"]}
- ⭐ (1星): {self.config["stance_assessment"]["criteria"]["1_star"]}

## 資料目錄結構

```
data/
├── raw/                    # 原始資料
│   ├── news/              # 新聞原始資料
│   └── search_results/    # 搜尋結果
├── processed/             # 處理後資料
│   ├── entities/          # 實體資料庫
│   ├── stances/           # 立場追蹤
│   └── graph/             # 圖形資料庫
└── reports/               # 分析報告
    ├── daily/            # 日報
    ├── monthly/          # 月報
    └── entities/         # 實體報告
```

## 每日工作流程

### 1. 執行新聞搜尋（建議每天早上 9-10 點）

使用關鍵字群組搜尋過去 24 小時的新聞：

```
Group A: 受害者家屬權益
Group B: 司法不公議題
Group C: 人權團體活動
Group D: 立法與司法改善
```

### 2. 實體識別與立場標記

- 識別新聞中的關鍵人物（立委、法官、律師、NPO 代表）
- 標記發言立場（⭐星級系統）
- 建立或更新人物檔案

### 3. 關係圖更新

- 記錄人物間的互動（聯合聲明、公開辯論等）
- 更新實體關係網絡
- 匯出視覺化圖表

### 4. 產出日報

- 新增新聞摘要
- 人物立場更新摘要
- 關係網絡變化摘要

## 重要功能

### 1. 實體管理（Entity Management）

```python
# 新增人物
python scripts/graph_db.py --add-node "person_name" \\
    --name "姓名" --type person --role "角色" --stance 5

# 查詢關係網絡
python scripts/graph_db.py --query-network "person_name" --depth 2

# 匯出視覺化
python scripts/export_graph.py
```

### 2. 立場追蹤（Stance Tracking）

- 記錄每次公開發言的立場傾向
- 追蹤立場變化歷程
- 識別關鍵影響者

### 3. 資料匯出

匯出格式：
- `stakeholders_cytoscape.json` - 網站互動圖
- `stakeholders_d3.json` - D3.js 力導向圖
- `stakeholders.graphml` - Neo4j/Gephi
- `stakeholders_nodes.csv` / `stakeholders_edges.csv` - CSV 資料表

## 與 Budget Tracker 協作

### 整合使用情境

**情境：NPO 金流與立場交叉驗證**

1. News Tracker: 搜尋「廢死聯盟」新聞發言，標記立場
2. Budget Tracker: 查詢該 NPO 接受的政府補助
3. 整合分析: 交叉比對補助時間與立場變化

**資料格式相容**：
- 統一 Node ID 命名規則
- 支援圖譜資料合併
- 建立人物對照表

## 設定檔位置

- 主要設定: `config/init_config.json`
- 搜尋模板: `data/raw/search_templates.json`
- 實體資料庫: `data/processed/entities/entity_registry.json`
- 立場追蹤: `data/processed/stances/stance_registry.json`

## 注意事項

1. **資料隱私**: 遵守《個人資料保護法》，僅收集公開發言
2. **新聞版權**: 摘要引用時注意合理使用範圍
3. **立場評估**: 基於公開發言，避免主觀臆測
4. **交叉驗證**: 重要資訊建議多來源比對

---

*此報告由初始化腳本自動產生*
"""

        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_content)

        print(f"   ✅ 報告已產生: {report_file}")


def main():
    """主程式"""
    initializer = NewsTrackerInitializer()

    print("\n" + "=" * 60)
    print("Victim Rights News Tracker - 初始化")
    print("=" * 60)

    print("\n準備執行第一次新聞資料收集...")
    print(f"追蹤 NPO: {', '.join(initializer.config['target_np_os'])}")
    print(f"追蹤人物: {', '.join(initializer.config['target_persons'])}")
    print(f"關鍵字群組: {len(initializer.config['search_keywords'])} 組\n")

    # 自動執行
    initializer.run_first_collection()


if __name__ == "__main__":
    main()
