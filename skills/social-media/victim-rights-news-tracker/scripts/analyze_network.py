#!/usr/bin/env python3
"""
關係網絡分析報告產生器

分析利害關係人網絡，產生以下報告:
- 關鍵行為者識別 (degree centrality)
- 關係強度分析
- 互動類別分布
- 網絡密度與結構指標
"""

import sqlite3
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

sys_path_inserted = False
import sys

# Ensure we can import graph_db
scripts_dir = Path(__file__).parent
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))
    sys_path_inserted = True

from graph_db import GraphDatabase, EXPORT_PATH

REPORT_PATH = EXPORT_PATH / "network_analysis_report.md"


def calculate_degree_centrality(db: GraphDatabase) -> dict:
    """計算節點的 degree centrality (連接數)"""
    with sqlite3.connect(str(db.db_path)) as conn:
        cursor = conn.cursor()

        # 計算每個節點的連接數
        cursor.execute("""
            SELECT source as node, COUNT(*) as count FROM edges GROUP BY source
            UNION ALL
            SELECT target as node, COUNT(*) as count FROM edges GROUP BY target
        """)

        degrees = defaultdict(int)
        for node, count in cursor.fetchall():
            degrees[node] += count

        return dict(degrees)


def analyze_relationship_strength(db: GraphDatabase) -> dict:
    """分析關係強度分布"""
    edges = db.get_all_edges()

    strength_ranges = {
        "高 (0.8-1.0)": 0,
        "中-高 (0.6-0.8)": 0,
        "中 (0.4-0.6)": 0,
        "低-中 (0.2-0.4)": 0,
        "低 (0.0-0.2)": 0,
    }

    strong_relationships = []

    for edge in edges:
        s = edge.strength or 0.5
        if s >= 0.8:
            strength_ranges["高 (0.8-1.0)"] += 1
            strong_relationships.append((edge.source, edge.target, s, edge.type))
        elif s >= 0.6:
            strength_ranges["中-高 (0.6-0.8)"] += 1
            strong_relationships.append((edge.source, edge.target, s, edge.type))
        elif s >= 0.4:
            strength_ranges["中 (0.4-0.6)"] += 1
        elif s >= 0.2:
            strength_ranges["低-中 (0.2-0.4)"] += 1
        else:
            strength_ranges["低 (0.0-0.2)"] += 1

    return {
        "distribution": strength_ranges,
        "strong_relationships": sorted(strong_relationships, key=lambda x: -x[2]),
    }


def analyze_interaction_categories(db: GraphDatabase) -> dict:
    """分析互動類別分布"""
    edges = db.get_all_edges()

    categories: dict = {}

    for edge in edges:
        cat = edge.interaction_category or "general"
        if cat not in categories:
            categories[cat] = {"count": 0, "types": set(), "avg_strength": []}
        categories[cat]["count"] += 1
        categories[cat]["types"].add(edge.type)
        categories[cat]["avg_strength"].append(edge.strength or 0.5)

    result = {}
    for cat, data in categories.items():
        avg_str = 0.0
        if data["avg_strength"]:
            avg_str = sum(data["avg_strength"]) / len(data["avg_strength"])
        result[cat] = {
            "count": data["count"],
            "edge_types": list(data["types"]),
            "avg_strength": avg_str,
        }

    return result


def identify_key_actors(db: GraphDatabase, degrees: dict) -> list:
    """識別關鍵行為者"""
    nodes = db.get_all_nodes()

    # 合併節點資訊與 centrality
    actors = []
    for node in nodes:
        degree = degrees.get(node.id, 0)
        actors.append(
            {
                "id": node.id,
                "name": node.name,
                "type": node.type,
                "party": node.party,
                "stance": node.stance,
                "degree": degree,
                "score": degree * (node.stance or 1),  # 綜合分數
            }
        )

    # 按 degree 和 score 排序
    return sorted(actors, key=lambda x: (-x["degree"], -x["score"]))


def calculate_network_metrics(db: GraphDatabase, degrees: dict) -> dict:
    """計算網絡整體指標"""
    edges = db.get_all_edges()
    nodes_count = len(db.get_all_nodes())
    edges_count = len(edges)

    # 網絡密度 (density) = 2 * E / (N * (N-1))
    if nodes_count > 1:
        density = (2 * edges_count) / (nodes_count * (nodes_count - 1))
    else:
        density = 0

    # 平均 degree
    avg_degree = sum(degrees.values()) / len(degrees) if degrees else 0

    # 最大 degree (hub)
    max_degree = max(degrees.values()) if degrees else 0

    # 已驗證邊緣比例
    verified_count = sum(1 for e in edges if e.verified)
    verified_ratio = verified_count / len(edges) if edges else 0

    return {
        "nodes_count": nodes_count,
        "edges_count": edges_count,
        "density": round(density, 3),
        "avg_degree": round(avg_degree, 2),
        "max_degree": max_degree,
        "verified_ratio": round(verified_ratio, 2),
    }


def generate_analysis_report():
    """產生完整分析報告"""
    print("🔍 開始分析利害關係人網絡...\n")

    db = GraphDatabase()

    # 收集分析數據
    print("📊 計算網絡指標...")
    degrees = calculate_degree_centrality(db)
    metrics = calculate_network_metrics(db, degrees)

    print("📊 分析關係強度...")
    strength_analysis = analyze_relationship_strength(db)

    print("📊 分析互動類別...")
    category_analysis = analyze_interaction_categories(db)

    print("📊 識別關鍵行為者...")
    key_actors = identify_key_actors(db, degrees)

    # 產生報告
    print("\n📝 產生分析報告...")

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("# 利害關係人網絡分析報告\n\n")
        f.write(f"**分析時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # 執行摘要
        f.write("## 📋 執行摘要\n\n")
        f.write(f"- **總節點數**: {metrics['nodes_count']}\n")
        f.write(f"- **總關係數**: {metrics['edges_count']}\n")
        f.write(f"- **網絡密度**: {metrics['density']}\n")
        f.write(f"- **平均連接數**: {metrics['avg_degree']}\n")
        f.write(f"- **最大連接數**: {metrics['max_degree']}\n")
        f.write(f"- **已驗證關係比例**: {metrics['verified_ratio'] * 100:.0f}%\n\n")

        # 關鍵行為者
        f.write("## 🎯 關鍵行為者 (Top 5)\n\n")
        f.write("| 排名 | 名稱 | 類型 | 政黨 | 立場 | 連接數 |\n")
        f.write("|------|------|------|------|------|--------|\n")
        for i, actor in enumerate(key_actors[:5], 1):
            stance_stars = "⭐" * actor["stance"] if actor["stance"] > 0 else "未評估"
            f.write(
                f"| {i} | {actor['name']} | {actor['type']} | {actor['party'] or '-'} | {stance_stars} | {actor['degree']} |\n"
            )
        f.write("\n")

        # 關係強度分析
        f.write("## 💪 關係強度分析\n\n")
        f.write("### 強度分布\n\n")
        f.write("| 強度區間 | 數量 | 比例 |\n")
        f.write("|----------|------|------|\n")
        total_edges = sum(strength_analysis["distribution"].values())
        for range_name, count in strength_analysis["distribution"].items():
            ratio = count / total_edges * 100 if total_edges > 0 else 0
            f.write(f"| {range_name} | {count} | {ratio:.1f}% |\n")
        f.write("\n")

        if strength_analysis["strong_relationships"]:
            f.write("### 強關係 Top 5\n\n")
            f.write("| 來源 | 目標 | 強度 | 類型 |\n")
            f.write("|------|------|------|------|\n")
            for source, target, strength, edge_type in strength_analysis[
                "strong_relationships"
            ][:5]:
                f.write(f"| {source} | {target} | {strength:.2f} | {edge_type} |\n")
            f.write("\n")

        # 互動類別分析
        f.write("## 📂 互動類別分析\n\n")
        f.write("| 類別 | 數量 | 邊緣類型 | 平均強度 |\n")
        f.write("|------|------|----------|----------|\n")
        for cat, data in sorted(
            category_analysis.items(), key=lambda x: -x[1]["count"]
        ):
            types_str = ", ".join(data["edge_types"][:3])
            if len(data["edge_types"]) > 3:
                types_str += "..."
            f.write(
                f"| {cat} | {data['count']} | {types_str} | {data['avg_strength']:.2f} |\n"
            )
        f.write("\n")

        # 網絡結構視覺化
        f.write("## 🕸️ 網絡結構\n\n")
        f.write("```mermaid\n")
        f.write("graph TD\n")

        # 只顯示主要連接
        edges = db.get_all_edges()
        displayed_edges = 0
        for edge in edges:
            if edge.strength and edge.strength >= 0.6:
                source_name = next(
                    (n.name for n in db.get_all_nodes() if n.id == edge.source),
                    edge.source,
                )
                target_name = next(
                    (n.name for n in db.get_all_nodes() if n.id == edge.target),
                    edge.target,
                )
                f.write(
                    f"    {edge.source}[{source_name}] --{edge.type}--> {edge.target}[{target_name}]\n"
                )
                displayed_edges += 1

        f.write("```\n\n")

        # 洞察與建議
        f.write("## 💡 洞察與建議\n\n")

        # 根據分析結果產生洞察
        f.write("### 網絡特徵\n\n")
        if metrics["density"] < 0.3:
            f.write("- **稀疏網絡**: 關係密度較低，可能存在未被記錄的關係\n")
        elif metrics["density"] > 0.7:
            f.write("- **密集網絡**: 高度互連，資訊流通可能較快\n")
        else:
            f.write("- **中等密度**: 關係分布均衡\n")

        if metrics["verified_ratio"] < 0.5:
            f.write(
                f"- **驗證需求**: 僅 {metrics['verified_ratio'] * 100:.0f}% 關係已驗證，建議加強資料驗證\n"
            )

        f.write("\n### 建議行動\n\n")
        f.write("1. **強化核心關係**: 優先維護與關鍵行為者的連接\n")
        f.write("2. **擴展網絡覆蓋**: 尋找與現有節點有潛在關係的新行為者\n")
        f.write("3. **驗證關係品質**: 對高強度但未驗證的關係進行確認\n")
        f.write("4. **分類標準化**: 確保互動類別標記的一致性\n\n")

        f.write("---\n\n")
        f.write(f"*報告由 Graph Database Analysis Tool 產生*\n")

    print(f"✅ 報告已儲存: {REPORT_PATH}\n")

    # 輸出摘要到 console
    print("=" * 60)
    print("📊 分析摘要")
    print("=" * 60)
    print(f"\n網絡規模: {metrics['nodes_count']} 節點, {metrics['edges_count']} 邊緣")
    print(f"網絡密度: {metrics['density']}")
    print(f"已驗證關係: {metrics['verified_ratio'] * 100:.0f}%")
    print(f"\n關鍵行為者 Top 3:")
    for i, actor in enumerate(key_actors[:3], 1):
        print(
            f"  {i}. {actor['name']} (連接數: {actor['degree']}, 立場: {'⭐' * actor['stance'] if actor['stance'] > 0 else '未評估'})"
        )
    print(f"\n強關係數量 (≥0.6): {len(strength_analysis['strong_relationships'])}")
    print(f"主要互動類別: {', '.join(list(category_analysis.keys())[:3])}")


if __name__ == "__main__":
    try:
        generate_analysis_report()
    except Exception as e:
        print(f"\n❌ 分析失敗: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
