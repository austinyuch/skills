#!/usr/bin/env python3
"""
數據備份與維護工具 (Data Backup and Maintenance Tool)

提供定期備份、數據驗證、清理維護功能。
"""

import sqlite3
import shutil
import json
from datetime import datetime
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from graph_db import GraphDatabase, DB_PATH

BACKUP_PATH = Path(__file__).parent.parent / "backup"


def backup_database():
    """備份 SQLite 資料庫"""
    BACKUP_PATH.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_PATH / f"stakeholders_graph_{timestamp}.db"

    if DB_PATH.exists():
        shutil.copy2(DB_PATH, backup_file)
        print(f"✅ 資料庫已備份: {backup_file}")
        return str(backup_file)
    else:
        print("⚠️ 資料庫檔案不存在，無法備份")
        return None


def validate_database():
    """驗證資料庫完整性"""
    db = GraphDatabase()
    issues = []

    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()

        # 檢查孤立節點（無任何關係的節點）
        cursor.execute("""
            SELECT n.id, n.name, n.type 
            FROM nodes n 
            LEFT JOIN edges e ON n.id = e.source OR n.id = e.target 
            WHERE e.id IS NULL
        """)
        orphaned = cursor.fetchall()
        if orphaned:
            issues.append(f"⚠️ 發現 {len(orphaned)} 個孤立節點（無關係）：")
            for node in orphaned[:5]:  # 只顯示前5個
                issues.append(f"   - {node[1]} ({node[0]})")

        # 檢查重複節點名稱
        cursor.execute("""
            SELECT name, COUNT(*) as count 
            FROM nodes 
            GROUP BY name 
            HAVING count > 1
        """)
        duplicates = cursor.fetchall()
        if duplicates:
            issues.append(f"⚠️ 發現 {len(duplicates)} 個重複名稱的節點：")
            for name, count in duplicates:
                issues.append(f"   - '{name}' 出現 {count} 次")

        # 檢查無效的關係（指向不存在的節點）
        cursor.execute("""
            SELECT e.source, e.target 
            FROM edges e 
            LEFT JOIN nodes ns ON e.source = ns.id 
            LEFT JOIN nodes nt ON e.target = nt.id 
            WHERE ns.id IS NULL OR nt.id IS NULL
        """)
        invalid_edges = cursor.fetchall()
        if invalid_edges:
            issues.append(f"❌ 發現 {len(invalid_edges)} 個無效關係：")
            for edge in invalid_edges[:5]:
                issues.append(f"   - {edge[0]} -> {edge[1]}")

        # 檢查未評估立場的節點
        cursor.execute("""
            SELECT id, name, type 
            FROM nodes 
            WHERE stance = 0 OR stance IS NULL
        """)
        unassessed = cursor.fetchall()
        if unassessed:
            issues.append(f"ℹ️ 有 {len(unassessed)} 個節點未評估立場")

    if issues:
        print("\n".join(issues))
    else:
        print("✅ 資料庫驗證通過，無發現問題")

    return len(issues) == 0


def clean_old_backups(days=30):
    """清理超過指定天數的舊備份"""
    if not BACKUP_PATH.exists():
        return

    cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
    removed = 0

    for backup_file in BACKUP_PATH.glob("stakeholders_graph_*.db"):
        if backup_file.stat().st_mtime < cutoff:
            backup_file.unlink()
            removed += 1

    if removed > 0:
        print(f"🗑️ 已清理 {removed} 個超過 {days} 天的舊備份")


def export_backup_manifest():
    """匯出備份清單"""
    if not BACKUP_PATH.exists():
        return

    backups = []
    for backup_file in sorted(BACKUP_PATH.glob("stakeholders_graph_*.db")):
        stat = backup_file.stat()
        backups.append(
            {
                "file": backup_file.name,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "created": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            }
        )

    manifest_path = BACKUP_PATH / "backup_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(backups, f, ensure_ascii=False, indent=2)

    print(f"✅ 備份清單已匯出: {manifest_path}")
    return backups


def maintenance_report():
    """產生維護報告"""
    db = GraphDatabase()
    stats = db.get_statistics()

    report_path = (
        BACKUP_PATH / f"maintenance_report_{datetime.now().strftime('%Y%m%d')}.md"
    )

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# 資料庫維護報告\n\n")
        f.write(f"**產生時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("## 資料統計\n\n")
        f.write(f"- 總節點數: {stats['total_nodes']}\n")
        f.write(f"- 總關係數: {stats['total_edges']}\n")
        f.write(f"- 總發言數: {stats['total_statements']}\n\n")

        f.write("### 節點類型分布\n\n")
        for node_type, count in stats["node_types"].items():
            f.write(f"- {node_type}: {count}\n")

        f.write("\n### 立場分布\n\n")
        for stance, count in sorted(stats["stance_distribution"].items(), reverse=True):
            stars = "⭐" * stance if stance > 0 else "未評估"
            f.write(f"- {stars}: {count}\n")

        f.write("\n## 備份狀態\n\n")
        backups = export_backup_manifest()
        if backups:
            f.write(f"目前有 {len(backups)} 個備份檔案:\n\n")
            for backup in backups[-5:]:  # 只顯示最新的5個
                f.write(f"- {backup['file']} ({backup['size_mb']} MB)\n")
        else:
            f.write("目前無備份檔案\n")

    print(f"✅ 維護報告已產生: {report_path}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="資料庫備份與維護工具")
    parser.add_argument("--backup", action="store_true", help="執行備份")
    parser.add_argument("--validate", action="store_true", help="驗證資料庫完整性")
    parser.add_argument(
        "--clean", type=int, metavar="DAYS", help="清理指定天數前的舊備份"
    )
    parser.add_argument("--report", action="store_true", help="產生維護報告")
    parser.add_argument("--all", action="store_true", help="執行所有維護操作")

    args = parser.parse_args()

    if args.all or args.backup:
        backup_database()

    if args.all or args.validate:
        validate_database()

    if args.all or args.clean:
        clean_old_backups(args.clean or 30)

    if args.all or args.report:
        maintenance_report()

    if not any([args.backup, args.validate, args.clean, args.report, args.all]):
        parser.print_help()


if __name__ == "__main__":
    main()
