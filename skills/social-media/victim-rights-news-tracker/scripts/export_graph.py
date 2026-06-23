#!/usr/bin/env python3
"""
圖形資料匯出工具 - 增強版

提供一鍵匯出所有格式的功能，支援篩選與強度計算
"""

import argparse
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from graph_db import GraphDatabase, EXPORT_PATH


def export_all(
    calculate_strength: bool = False,
    min_strength: Optional[float] = None,
    verified_only: bool = False,
    interaction_category: Optional[str] = None,
):
    db = GraphDatabase()
    EXPORT_PATH.mkdir(exist_ok=True)

    print("🔄 開始匯出所有格式...\n")

    if calculate_strength:
        print("⚙️  正在自動計算關係強度...")
        count = db.auto_calculate_all_strengths()
        print(f"✅ 已更新 {count} 個邊緣的強度\n")

    cytoscape_path = EXPORT_PATH / "stakeholders_cytoscape.json"
    db.export_to_cytoscape(str(cytoscape_path))
    print(f"✅ Cytoscape.js: {cytoscape_path}")
    print("   用途：網站前端互動式圖表\n")

    d3_path = EXPORT_PATH / "stakeholders_d3.json"
    db.export_to_d3(str(d3_path))
    print(f"✅ D3.js: {d3_path}")
    print("   用途：網站前端力導向圖\n")

    graphml_path = EXPORT_PATH / "stakeholders.graphml"
    db.export_to_graphml(str(graphml_path))
    print(f"✅ GraphML: {graphml_path}")
    print("   用途：Neo4j、Gephi、Cytoscape Desktop\n")

    nodes_path, edges_path = db.export_to_csv(str(EXPORT_PATH / "stakeholders"))
    print(f"✅ CSV 節點: {nodes_path}")
    print(f"✅ CSV 關係: {edges_path}")
    print("   用途：Excel 分析、資料庫匯入\n")

    filtered_edges = []
    filter_desc = []

    if min_strength is not None or verified_only or interaction_category:
        print("📋 產生篩選匯出報告...")

        filtered_edges = db.get_all_edges(
            min_strength=min_strength,
            verified_only=verified_only,
            interaction_category=interaction_category,
        )

        if min_strength is not None:
            filter_desc.append(f"強度≥{min_strength}")
        if verified_only:
            filter_desc.append("已驗證")
        if interaction_category:
            filter_desc.append(f"類別={interaction_category}")

        filter_report_path = EXPORT_PATH / "filtered_edges_report.md"
        with open(filter_report_path, "w", encoding="utf-8") as f:
            f.write(f"# 篩選邊緣報告\n\n")
            f.write(f"**篩選條件**: {', '.join(filter_desc)}\n\n")
            f.write(f"**符合條件的邊緣數**: {len(filtered_edges)}\n\n")
            f.write("## 邊緣列表\n\n")
            f.write("| 來源 | 目標 | 類型 | 強度 | 類別 | 驗證 |\n")
            f.write("|------|------|------|------|------|------|\n")
            for edge in filtered_edges:
                verified_mark = "✓" if edge.verified else "✗"
                f.write(
                    f"| {edge.source} | {edge.target} | {edge.type} | {edge.strength} | {edge.interaction_category} | {verified_mark} |\n"
                )

        print(f"✅ 篩選報告: {filter_report_path}")
        print(f"   符合條件的邊緣數: {len(filtered_edges)}\n")

    stats = db.get_statistics()
    report_path = EXPORT_PATH / "graph_export_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# 圖形資料庫匯出報告\n\n")
        f.write(f"**匯出時間**：{stats['last_updated']}\n\n")
        f.write("## 匯出檔案清單\n\n")
        f.write("### 網站視覺化格式\n")
        f.write(f"- **Cytoscape.js**: `stakeholders_cytoscape.json`\n")
        f.write(f"  - 適用於：互動式網路圖、節點可拖曳、可點擊\n")
        f.write(f"  - 使用套件：[Cytoscape.js](https://js.cytoscape.org/)\n\n")
        f.write(f"- **D3.js**: `stakeholders_d3.json`\n")
        f.write(f"  - 適用於：力導向圖、動態視覺化\n")
        f.write(f"  - 使用套件：[D3.js](https://d3js.org/)\n\n")
        f.write("### 專業圖形工具格式\n")
        f.write(f"- **GraphML**: `stakeholders.graphml`\n")
        f.write(f"  - 適用於：Neo4j、Gephi、Cytoscape Desktop\n")
        f.write(f"  - 說明：標準 XML 圖形格式，含完整節點屬性\n\n")
        f.write("### 資料分析格式\n")
        f.write(f"- **CSV 節點**: `stakeholders_nodes.csv`\n")
        f.write(f"- **CSV 關係**: `stakeholders_edges.csv`\n")
        f.write(f"  - 適用於：Excel、Pandas、R、其他資料分析工具\n\n")

        if min_strength is not None or verified_only or interaction_category:
            f.write("### 篩選報告\n")
            f.write(f"- **篩選條件**: {', '.join(filter_desc)}\n")
            f.write(f"- **符合邊緣數**: {len(filtered_edges)}\n\n")

        f.write("## 資料統計\n\n")
        f.write(f"- 總節點數：{stats['total_nodes']}\n")
        f.write(f"- 總關係數：{stats['total_edges']}\n")
        f.write(f"- 總發言數：{stats['total_statements']}\n\n")
        f.write("### 節點類型分布\n")
        for node_type, count in stats["node_types"].items():
            f.write(f"- {node_type}: {count}\n")
        f.write("\n")
        f.write("### 立場分布\n")
        for stance, count in sorted(stats["stance_distribution"].items(), reverse=True):
            stars = "⭐" * stance
            f.write(f"- {stars} ({stance}): {count}\n")
        f.write("\n")
        f.write("### 邊緣類型分布\n")
        for edge_type, count in stats.get("edge_types", {}).items():
            f.write(f"- {edge_type}: {count}\n")
        f.write("\n")

    print(f"✅ 匯出報告: {report_path}\n")

    print("=" * 60)
    print("🎉 所有格式匯出完成！")
    print("=" * 60)
    print(f"\n📁 匯出目錄：{EXPORT_PATH}")
    print(f"\n📊 資料統計：")
    print(f"   - 節點數：{stats['total_nodes']}")
    print(f"   - 關係數：{stats['total_edges']}")
    print(f"   - 發言數：{stats['total_statements']}")
    print("\n💡 下一步：")
    print("   1. 將 cytoscape/d3 JSON 檔案用於網站前端視覺化")
    print("   2. 將 GraphML 匯入 Neo4j/Gephi 進行進階分析")
    print("   3. 使用 CSV 在 Excel 中進行資料分析")


def main():
    parser = argparse.ArgumentParser(
        description="圖形資料庫匯出工具 - 增強版",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python export_graph.py
    python export_graph.py --calculate-strength
    python export_graph.py --min-strength 0.7
    python export_graph.py --verified-only
    python export_graph.py --category public_action
    python export_graph.py --calculate-strength --min-strength 0.6 --verified-only
        """,
    )

    parser.add_argument(
        "--calculate-strength", action="store_true", help="自動計算所有邊緣的關係強度"
    )

    parser.add_argument(
        "--min-strength", type=float, default=None, help="最小關係強度篩選 (0.0-1.0)"
    )

    parser.add_argument(
        "--verified-only", action="store_true", help="只匯出已驗證的邊緣"
    )

    parser.add_argument(
        "--category",
        type=str,
        default=None,
        help="篩選特定互動類別 (public_action, legislative, media, legal, organizational, social)",
    )

    args = parser.parse_args()

    export_all(
        calculate_strength=args.calculate_strength,
        min_strength=args.min_strength,
        verified_only=args.verified_only,
        interaction_category=args.category,
    )


if __name__ == "__main__":
    main()
