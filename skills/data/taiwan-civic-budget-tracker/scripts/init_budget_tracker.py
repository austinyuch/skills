#!/usr/bin/env python3
"""
Taiwan Civic Budget Tracker - Initialization Script
第一次初始化與資料收集
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


class BudgetTrackerInitializer:
    """預算追蹤系統初始化器"""

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
            "data_sources": {
                "pcc_opendata": {
                    "enabled": True,
                    "last_update": None,
                    "update_frequency": "daily",
                },
                "moea_company": {
                    "enabled": True,
                    "last_update": None,
                    "update_frequency": "weekly",
                },
                "judicial_judges": {
                    "enabled": True,
                    "last_update": None,
                    "update_frequency": "monthly",
                },
                "moj_lawyers": {
                    "enabled": True,
                    "last_update": None,
                    "update_frequency": "weekly",
                },
            },
            "target_agencies": [
                "司法院",
                "法務部",
                "法務部調查局",
                "矯正署",
                "法律扶助基金會",
            ],
            "keywords": [
                "司法改革",
                "修復式司法",
                "國民法官",
                "人民參審",
                "人權宣導",
                "法律扶助",
                "犯罪預防",
                "更生保護",
                "廢除死刑",
                "死刑",
                "刑罰",
                "獄政",
            ],
            "entity_resolution": {
                "require_birth_year": True,
                "similarity_threshold": 0.85,
                "fuzzy_match_enabled": True,
            },
            "first_collection": {
                "date_range": {"start": "2020-01-01", "end": "2024-12-31"},
                "status": "pending",
            },
        }

        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)

        return default_config

    def setup_directories(self):
        """設定目錄結構"""
        directories = [
            DATA_DIR / "raw" / "pcc",
            DATA_DIR / "raw" / "moea",
            DATA_DIR / "raw" / "judicial",
            DATA_DIR / "raw" / "moj",
            DATA_DIR / "processed" / "entities",
            DATA_DIR / "processed" / "relationships",
            DATA_DIR / "reports" / "procurement",
            DATA_DIR / "reports" / "analysis",
            PROJECT_ROOT / "logs",
            PROJECT_ROOT / "export",
            PROJECT_ROOT / "backup",
            PROJECT_ROOT / "temp",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"✅ 目錄已建立: {directory}")

    def run_first_collection(self):
        """執行第一次資料收集"""
        print("\n" + "=" * 60)
        print("🚀 Taiwan Civic Budget Tracker - 第一次資料收集")
        print("=" * 60 + "\n")

        # 1. 收集標案資料
        print("📦 Phase 1: 收集標案資料...")
        self._collect_procurement_data()

        # 2. 收集公司資料
        print("\n📦 Phase 2: 收集公司資料...")
        self._collect_company_data()

        # 3. 收集法律人資料
        print("\n📦 Phase 3: 收集法律專業人員資料...")
        self._collect_legal_professionals()

        # 4. 建立實體關係
        print("\n🔗 Phase 4: 建立實體關係...")
        self._build_relationships()

        # 5. 產生初始報告
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
        print("   1. 查看 reports/init_report.md 了解收集結果")
        print("   2. 執行 python scripts/network_analysis.py 分析關係網絡")
        print("   3. 執行 python scripts/visualization.py 產生視覺化圖表")

    def _collect_procurement_data(self):
        """收集標案資料（簡化版）"""
        try:
            # 這裡應該呼叫 scripts/collect_procurement.py
            # 為了示範，建立一個空的資料檔案
            output_file = (
                RAW_DIR / "pcc" / f"procurement_init_{datetime.now():%Y%m%d}.json"
            )

            # 模擬資料結構
            sample_data = {
                "collection_date": datetime.now().isoformat(),
                "source": "PCC",
                "target_keywords": self.config["keywords"],
                "target_agencies": self.config["target_agencies"],
                "data": [],  # 實際資料會在執行爬蟲後填入
                "status": "initialized",
            }

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(sample_data, f, ensure_ascii=False, indent=2)

            print(f"   ✅ 標案資料初始化: {output_file}")
            print(f"   📌 目標關鍵字: {', '.join(self.config['keywords'][:3])}...")
            print(f"   📌 目標機關: {', '.join(self.config['target_agencies'][:3])}...")

        except Exception as e:
            print(f"   ❌ 標案資料收集失敗: {e}")

    def _collect_company_data(self):
        """收集公司資料（簡化版）"""
        try:
            output_file = (
                RAW_DIR / "moea" / f"companies_init_{datetime.now():%Y%m%d}.json"
            )

            sample_data = {
                "collection_date": datetime.now().isoformat(),
                "source": "MOEA",
                "note": "需要手動下載經濟部開放資料或執行爬蟲",
                "data": [],
                "status": "initialized",
            }

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(sample_data, f, ensure_ascii=False, indent=2)

            print(f"   ✅ 公司資料初始化: {output_file}")
            print(f"   💡 提示：請參考 references/data-sources.md 下載商工登記資料")

        except Exception as e:
            print(f"   ❌ 公司資料收集失敗: {e}")

    def _collect_legal_professionals(self):
        """收集法律專業人員資料"""
        try:
            # 律師資料
            lawyer_file = RAW_DIR / "moj" / f"lawyers_init_{datetime.now():%Y%m%d}.json"
            lawyer_data = {
                "collection_date": datetime.now().isoformat(),
                "source": "MOJ_Lawyer_Query",
                "url": "https://lawyerbc.moj.gov.tw/",
                "note": "可使用關鍵字批次查詢律師",
                "target_lawyers": [],  # 從標案判決書中提取的律師名單
                "status": "initialized",
            }

            with open(lawyer_file, "w", encoding="utf-8") as f:
                json.dump(lawyer_data, f, ensure_ascii=False, indent=2)

            print(f"   ✅ 律師資料初始化: {lawyer_file}")

            # 法官資料
            judge_file = (
                RAW_DIR / "judicial" / f"judges_init_{datetime.now():%Y%m%d}.json"
            )
            judge_data = {
                "collection_date": datetime.now().isoformat(),
                "source": "Judicial_Yuan",
                "url": "https://www.judicial.gov.tw/",
                "note": "從法官事務分配頁面收集",
                "courts": [
                    "最高法院",
                    "臺灣高等法院",
                    "臺北地方法院",
                    "臺中地方法院",
                    "高雄地方法院",
                ],
                "status": "initialized",
            }

            with open(judge_file, "w", encoding="utf-8") as f:
                json.dump(judge_data, f, ensure_ascii=False, indent=2)

            print(f"   ✅ 法官資料初始化: {judge_file}")

        except Exception as e:
            print(f"   ❌ 法律人資料收集失敗: {e}")

    def _build_relationships(self):
        """建立實體關係"""
        try:
            rel_file = (
                PROCESSED_DIR
                / "relationships"
                / f"relationships_init_{datetime.now():%Y%m%d}.json"
            )

            relationship_template = {
                "creation_date": datetime.now().isoformat(),
                "entity_types": {
                    "GovernmentAgency": "政府機關",
                    "BudgetPlan": "預算計畫",
                    "ProcurementCase": "標案",
                    "Company": "廠商",
                    "Person": "人員",
                    "Lawyer": "律師",
                    "Judge": "法官",
                    "Subsidy": "補助",
                },
                "relationship_types": [
                    {"type": "BUDGET_FOR", "description": "機關編列預算給計畫"},
                    {"type": "PROCURES", "description": "計畫透過標案執行"},
                    {"type": "AWARDED_TO", "description": "標案決標給廠商"},
                    {"type": "OWNS", "description": "公司投資關係"},
                    {"type": "DIRECTS", "description": "人員擔任董監事"},
                    {"type": "RECEIVES", "description": "NPO接受補助"},
                    {"type": "REPRESENTS", "description": "律師代表當事人"},
                    {"type": "PRESIDES", "description": "法官審理案件"},
                ],
                "data": [],
                "status": "template_created",
            }

            with open(rel_file, "w", encoding="utf-8") as f:
                json.dump(relationship_template, f, ensure_ascii=False, indent=2)

            print(f"   ✅ 關係模板建立: {rel_file}")
            print(
                f"   📊 定義 {len(relationship_template['relationship_types'])} 種關係類型"
            )

        except Exception as e:
            print(f"   ❌ 關係建立失敗: {e}")

    def _generate_init_report(self):
        """產生初始化報告"""
        report_file = REPORTS_DIR / f"init_report_{datetime.now():%Y%m%d}.md"

        report_content = f"""# Taiwan Civic Budget Tracker 初始化報告

**初始化日期**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 系統設定

### 目標機關
{chr(10).join(f"- {agency}" for agency in self.config["target_agencies"])}

### 追蹤關鍵字
{chr(10).join(f"- {keyword}" for keyword in self.config["keywords"])}

### 資料來源設定

| 來源 | 狀態 | 更新頻率 |
|------|------|---------|
| PCC 標案開放資料 | ✅ 啟用 | 每日 |
| 商工登記資料 | ✅ 啟用 | 每週 |
| 法官事務分配 | ✅ 啟用 | 每月 |
| 法務部律師查詢 | ✅ 啟用 | 每週 |

## 資料目錄結構

```
data/
├── raw/                    # 原始資料
│   ├── pcc/               # 標案資料
│   ├── moea/              # 公司資料
│   ├── judicial/          # 法官資料
│   └── moj/               # 律師資料
├── processed/             # 處理後資料
│   ├── entities/          # 實體資料
│   └── relationships/     # 關係資料
└── reports/               # 分析報告
    ├── procurement/       # 標案報告
    └── analysis/          # 分析報告
```

## 接下來的步驟

### 1. 執行資料收集

```bash
# 收集標案資料（建議從這裡開始）
python scripts/collect_procurement.py

# 收集公司資料
python scripts/collect_company_data.py

# 查詢律師資料
python scripts/query_lawyers.py
```

### 2. 執行分析

```bash
# 建立關係網絡
python scripts/network_analysis.py

# 產生視覺化圖表
python scripts/visualization.py
```

### 3. 查看結果

- 標案分析報告：`data/reports/procurement/`
- 關係網絡圖：`export/`
- 日誌檔案：`logs/`

## 重要提醒

1. **資料隱私**: 遵守《個人資料保護法》，僅收集公開職務相關資訊
2. **反爬蟲**: 政府網站有查詢限制，請降低請求頻率
3. **同名異人**: 人員實體必須有「姓名 + 出生年」才能準確識別
4. **資料驗證**: 建議交叉比對多個來源，確保資料準確性

## 設定檔位置

- 主要設定: `config/init_config.json`
- 實體命名規則: `references/entity-management-guide.md`
- 資料來源說明: `references/data-sources.md`

---

*此報告由初始化腳本自動產生*
"""

        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_content)

        print(f"   ✅ 報告已產生: {report_file}")


def main():
    """主程式"""
    initializer = BudgetTrackerInitializer()

    print("\n" + "=" * 60)
    print("Taiwan Civic Budget Tracker - 初始化")
    print("=" * 60)

    # 詢問是否執行第一次資料收集
    print("\n準備執行第一次資料收集...")
    print(
        f"目標時間範圍: {initializer.config['first_collection']['date_range']['start']} ~ {initializer.config['first_collection']['date_range']['end']}"
    )
    print(f"目標機關: {', '.join(initializer.config['target_agencies'])}")
    print(f"追蹤關鍵字: {len(initializer.config['keywords'])} 個\n")

    # 自動執行（在自動化環境中）
    initializer.run_first_collection()


if __name__ == "__main__":
    main()
