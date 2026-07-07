#!/usr/bin/env python3
"""
圖形資料庫遷移腳本

Phase 4 & 5: 更新資料庫結構並遷移現有數據
- 新增邊緣屬性欄位 (strength, direction, verified, evidence_count, first_seen, sentiment, interaction_category)
- 將現有的 "interact" 類型邊緣遷移到更具體的類型
"""

import sqlite3
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from graph_db import GraphDatabase, EDGE_TYPES, INTERACTION_CATEGORIES
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data"
DB_PATH = DATA_PATH / "stakeholders_graph.db"


def migrate_database():
    """執行資料庫遷移"""
    print("🔧 開始資料庫遷移...\n")

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Phase 4: 檢查並新增欄位
    print("📋 Phase 4: 檢查並更新資料表結構")

    # 取得現有欄位
    cursor.execute("PRAGMA table_info(edges)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    new_columns = {
        "strength": ("REAL", 0.5),
        "direction": ("TEXT", "undirected"),
        "verified": ("INTEGER", 0),
        "evidence_count": ("INTEGER", 1),
        "first_seen": ("TEXT", None),
        "sentiment": ("REAL", None),
        "interaction_category": ("TEXT", "general"),
    }

    for col_name, (col_type, default_val) in new_columns.items():
        if col_name not in existing_columns:
            print(f"  ➕ 新增欄位: {col_name} ({col_type})")
            if default_val is not None:
                cursor.execute(
                    f"ALTER TABLE edges ADD COLUMN {col_name} {col_type} DEFAULT {repr(default_val)}"
                )
            else:
                cursor.execute(f"ALTER TABLE edges ADD COLUMN {col_name} {col_type}")
        else:
            print(f"  ✓ 欄位已存在: {col_name}")

    conn.commit()
    print("\n✅ Phase 4 完成: 資料表結構已更新\n")

    # Phase 5: 遷移現有 "interact" 邊緣到具體類型
    print("📋 Phase 5: 遷移現有邊緣類型")

    # 取得所有 "interact" 類型的邊緣
    cursor.execute("""
        SELECT rowid, source, target, type, interaction_type, description
        FROM edges
        WHERE type = 'interact'
    """)
    interact_edges = cursor.fetchall()

    if not interact_edges:
        print("  ✓ 沒有需要遷移的 'interact' 類型邊緣\n")
    else:
        print(f"  📝 發現 {len(interact_edges)} 個 'interact' 類型邊緣需要遷移\n")

        # 類型映射規則 (根據 interaction_type 和 description 推斷)
        type_mapping = {
            "組織": "organize",
            "參與": "participate",
            "出席": "participate",
            "記者": "participate",
            "陪同": "participate",
            "一起": "participate",
            "共同": "participate",
            "發起": "organize",
            "支持": "support",
            "協助": "support",
            "協同": "support",
            "提案": "propose",
            "建議": "propose",
            "倡議": "propose",
            "代表": "represent",
            "發言": "represent",
            "提及": "mention",
            "說明": "mention",
            "資金": "funds",
            "資助": "funds",
            "捐贈": "funds",
            "遊說": "lobby",
            "關注": "monitor",
            "監督": "monitor",
            "質詢": "inquiry",
            "辯論": "debate",
            "連署": "cosign",
            "聲援": "support",
            "協調": "coordinate",
            "溝通": "coordinate",
        }

        migrated_count = 0

        for edge in interact_edges:
            rowid, source, target, old_type, interaction_type, description = edge

            # 根據 interaction_type 或 description 推斷新類型
            new_type = "interact"  # 預設保留原類型

            # 檢查 interaction_type
            if interaction_type:
                interaction_lower = interaction_type.lower()
                for keyword, mapped_type in type_mapping.items():
                    if keyword in interaction_lower:
                        new_type = mapped_type
                        break

            # 如果沒有匹配，檢查 description
            if new_type == "interact" and description:
                desc_lower = description.lower()
                for keyword, mapped_type in type_mapping.items():
                    if keyword in desc_lower:
                        new_type = mapped_type
                        break

            # 自動分類 interaction_category
            category = "general"
            if new_type in ["organize", "participate", "coordinate", "cosign"]:
                category = "public_action"
            elif new_type in ["propose", "lobby", "inquiry"]:
                category = "legislative"
            elif new_type in ["represent", "mention", "debate"]:
                category = "media"
            elif new_type in ["funds", "support"]:
                category = "organizational"
            elif new_type in ["monitor"]:
                category = "social"

            # 更新邊緣
            cursor.execute(
                """
                UPDATE edges
                SET type = ?,
                    interaction_category = ?,
                    first_seen = COALESCE(first_seen, date),
                    strength = COALESCE(strength, 0.5)
                WHERE rowid = ?
            """,
                (new_type, category, rowid),
            )

            migrated_count += 1

            print(f"    {migrated_count}. {source} → {target}")
            print(f"       {old_type} → {new_type} (類別: {category})")
            if interaction_type:
                print(f"       互動: {interaction_type}")

        conn.commit()
        print(f"\n✅ Phase 5 完成: 已遷移 {migrated_count} 個邊緣\n")

    # 建立新索引
    print("📋 Phase 6: 建立新索引")

    indexes_to_create = [
        (
            "idx_edges_strength",
            "CREATE INDEX IF NOT EXISTS idx_edges_strength ON edges(strength)",
        ),
        (
            "idx_edges_category",
            "CREATE INDEX IF NOT EXISTS idx_edges_category ON edges(interaction_category)",
        ),
        (
            "idx_edges_verified",
            "CREATE INDEX IF NOT EXISTS idx_edges_verified ON edges(verified)",
        ),
    ]

    for idx_name, create_sql in indexes_to_create:
        cursor.execute(
            f"SELECT name FROM sqlite_master WHERE type='index' AND name='{idx_name}'"
        )
        if cursor.fetchone():
            print(f"  ✓ 索引已存在: {idx_name}")
        else:
            cursor.execute(create_sql)
            print(f"  ➕ 建立索引: {idx_name}")

    conn.commit()
    print("\n✅ Phase 6 完成: 索引已建立\n")

    # 驗證結果
    print("📋 Phase 7: 驗證遷移結果")

    cursor.execute("SELECT COUNT(*) FROM edges")
    total_edges = cursor.fetchone()[0]

    cursor.execute("SELECT type, COUNT(*) FROM edges GROUP BY type")
    edge_types_dist = dict(cursor.fetchall())

    cursor.execute(
        "SELECT interaction_category, COUNT(*) FROM edges GROUP BY interaction_category"
    )
    category_dist = dict(cursor.fetchall())

    print(f"  📊 總邊緣數: {total_edges}")
    print(f"\n  📊 邊緣類型分布:")
    for edge_type, count in sorted(edge_types_dist.items(), key=lambda x: -x[1]):
        print(f"    - {edge_type}: {count}")

    print(f"\n  📊 互動類別分布:")
    for category, count in sorted(category_dist.items(), key=lambda x: -x[1]):
        print(f"    - {category}: {count}")

    conn.close()
    print("\n✅ 資料庫遷移完成！")
    print(f"\n⏰ 完成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return True


if __name__ == "__main__":
    try:
        success = migrate_database()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 遷移失敗: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
