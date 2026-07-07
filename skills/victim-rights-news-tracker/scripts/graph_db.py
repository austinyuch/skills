#!/usr/bin/env python3
"""
本地圖形資料庫管理工具 (Local Graph Database Manager)

使用 SQLite 作為輕量級圖形資料庫，存儲人物、組織節點與其關係。
支援多種匯出格式供網站視覺化使用。

Features:
- 節點管理（人物、組織、案件）
- 關係管理（同盟、對立、上下級、互動）
- 立場追蹤（⭐星級評分）
- 多格式匯出（GraphML、Cytoscape.js JSON、D3.js JSON、CSV）

Usage:
    # 初始化資料庫
    python graph_db.py --init

    # 新增節點
    python graph_db.py --add-node "王婉諭" --type person --attrs '{"role":"立委","party":"時代力量","stance":5}'

    # 新增關係
    python graph_db.py --add-edge "王婉諭" "生命權平等協會" --type ally --attrs '{"interaction":"聯合記者會","date":"2024-01-15"}'

    # 匯出資料
    python graph_db.py --export --format cytoscape --output stakeholders.json
    python graph_db.py --export --format graphml --output stakeholders.graphml
    python graph_db.py --export --format d3 --output stakeholders-d3.json
    python graph_db.py --export --format csv --output stakeholders

    # 查詢關係網絡
    python graph_db.py --query-network "王婉諭" --depth 2

    # 統計報告
    python graph_db.py --stats
"""

import sqlite3
import json
import argparse
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path


# 資料庫路徑設定
DB_PATH = Path(__file__).parent.parent / "data" / "stakeholders_graph.db"
EXPORT_PATH = Path(__file__).parent.parent / "export"


@dataclass
class Node:
    """圖形節點（人物、組織、案件）"""

    id: str
    name: str
    type: str  # person, organization, party, case, official
    role: Optional[str] = None
    party: Optional[str] = None
    stance: int = 0  # 0-5 星級
    description: Optional[str] = None
    first_seen: Optional[str] = None
    last_updated: Optional[str] = None
    attributes: Optional[Dict] = None


@dataclass
class Edge:
    """圖形邊（關係）- 增強版"""

    source: str
    target: str
    type: str  # ally, oppose, interact, hierarchy, family, organize, participate, support, propose, represent, mention, funds, lobby
    interaction_type: Optional[str] = None  # 記者會、質詢、聲明等
    interaction_category: Optional[str] = (
        None  # public_action, legislative, media, legal, organizational
    )
    date: Optional[str] = None
    description: Optional[str] = None

    # 新增屬性
    strength: int = 3  # 1-5 關係強度
    direction: str = "bidirectional"  # outgoing, incoming, bidirectional
    verified: bool = True  # 是否已驗證
    evidence_count: int = 1  # 證據數量
    first_seen: Optional[str] = None  # 首次發現日期
    sentiment: str = "neutral"  # positive, neutral, negative

    attributes: Optional[Dict] = None


# 互動類型分類系統
INTERACTION_CATEGORIES = {
    "public_action": ["press_conference", "rally", "speech", "interview", "protest"],
    "legislative": ["propose_bill", "co_sign", "question", "debate", "amendment"],
    "media": ["mentioned", "quoted", "featured", "interviewed"],
    "legal": ["represent", "testify", "file_suit", "defend"],
    "organizational": ["found", "join", "lead", "speak_for", "resign"],
    "social": ["endorse", "criticize", "praise", "support"],
}

# 完整的 Edge 類型清單
EDGE_TYPES = [
    # 原有類型
    "ally",
    "oppose",
    "interact",
    "hierarchy",
    "family",
    # 新增細分類型
    "organize",  # 主辦活動
    "participate",  # 參與活動
    "support",  # 聲援/支持
    "propose",  # 提案/推動
    "represent",  # 代表/代理
    "mention",  # 被提及
    "funds",  # 資金關係
    "lobby",  # 遊說關係
    "endorse",  # 背書/支持
    "oppose_action",  # 反對行動
    "collaborate",  # 合作
    "influence",  # 影響
]

# 立場顏色對應
STANCE_COLORS = {
    5: "#FF6B6B",  # 強烈支持 - 紅色
    4: "#FFA07A",  # 支持 - 橘紅
    3: "#FFD93D",  # 中立 - 黃色
    2: "#6BCB77",  # 消極 - 綠色
    1: "#4D96FF",  # 反對 - 藍色
    0: "#95A5A6",  # 未評估 - 灰色
}

# 關係類型顏色
EDGE_TYPE_COLORS = {
    "ally": "#27ae60",  # 綠色 - 同盟
    "oppose": "#e74c3c",  # 紅色 - 對立
    "interact": "#95a5a6",  # 灰色 - 互動
    "organize": "#9b59b6",  # 紫色 - 主辦
    "participate": "#3498db",  # 藍色 - 參與
    "support": "#2ecc71",  # 亮綠 - 支持
    "propose": "#f39c12",  # 橙色 - 提案
    "hierarchy": "#34495e",  # 深灰 - 上下級
    "funds": "#e67e22",  # 深橙 - 資金
    "lobby": "#1abc9c",  # 青色 - 遊說
    "family": "#ff7979",  # 粉紅 - 家屬
    "represent": "#74b9ff",  # 淺藍 - 代表
    "mention": "#dfe6e9",  # 淺灰 - 提及
}

# 節點類型形狀
NODE_SHAPES = {
    "person": "ellipse",  # 圓形
    "organization": "round-rectangle",  # 圓角矩形
    "party": "hexagon",  # 六角形
    "official": "diamond",  # 菱形
    "case": "triangle",  # 三角形
}


class GraphDatabase:
    """SQLite 圖形資料庫管理類別"""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(DB_PATH)
        self._init_db()

    def _init_db(self):
        """初始化資料庫結構"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 節點表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS nodes (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    role TEXT,
                    party TEXT,
                    stance INTEGER DEFAULT 0,
                    description TEXT,
                    first_seen DATE,
                    last_updated DATE,
                    attributes TEXT
                )
            """)

            # 關係表（增強版）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS edges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    target TEXT NOT NULL,
                    type TEXT NOT NULL,
                    interaction_type TEXT,
                    interaction_category TEXT,  -- public_action, legislative, media, legal, organizational
                    date DATE,
                    description TEXT,
                    strength INTEGER DEFAULT 3,  -- 1-5 關係強度
                    direction TEXT DEFAULT 'bidirectional',  -- outgoing, incoming, bidirectional
                    verified BOOLEAN DEFAULT 1,  -- 是否已驗證
                    evidence_count INTEGER DEFAULT 1,  -- 證據數量
                    first_seen DATE,  -- 首次發現日期
                    sentiment TEXT DEFAULT 'neutral',  -- positive, neutral, negative
                    attributes TEXT,
                    FOREIGN KEY (source) REFERENCES nodes(id),
                    FOREIGN KEY (target) REFERENCES nodes(id)
                )
            """)

            # 發言記錄表（時間序列資料）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS statements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    node_id TEXT NOT NULL,
                    date DATE NOT NULL,
                    occasion TEXT,
                    content TEXT,
                    stance_mark INTEGER,
                    source_url TEXT,
                    source_media TEXT,
                    FOREIGN KEY (node_id) REFERENCES nodes(id)
                )
            """)

            # 創建索引（增強版）
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_nodes_party ON nodes(party)")
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_nodes_stance ON nodes(stance)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target)"
            )
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_edges_type ON edges(type)")
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_edges_strength ON edges(strength)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_edges_category ON edges(interaction_category)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_statements_node ON statements(node_id)"
            )

            conn.commit()

    def add_node(self, node: Node) -> bool:
        """新增或更新節點"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 檢查是否已存在
                cursor.execute("SELECT id FROM nodes WHERE id = ?", (node.id,))
                exists = cursor.fetchone()

                now = datetime.now().strftime("%Y-%m-%d")

                if exists:
                    # 更新現有節點
                    cursor.execute(
                        """
                        UPDATE nodes 
                        SET name = ?, type = ?, role = ?, party = ?, stance = ?,
                            description = ?, last_updated = ?, attributes = ?
                        WHERE id = ?
                    """,
                        (
                            node.name,
                            node.type,
                            node.role,
                            node.party,
                            node.stance,
                            node.description,
                            now,
                            json.dumps(node.attributes, ensure_ascii=False)
                            if node.attributes
                            else None,
                            node.id,
                        ),
                    )
                else:
                    # 新增節點
                    cursor.execute(
                        """
                        INSERT INTO nodes (id, name, type, role, party, stance, 
                                         description, first_seen, last_updated, attributes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            node.id,
                            node.name,
                            node.type,
                            node.role,
                            node.party,
                            node.stance,
                            node.description,
                            node.first_seen or now,
                            now,
                            json.dumps(node.attributes, ensure_ascii=False)
                            if node.attributes
                            else None,
                        ),
                    )

                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding node: {e}")
            return False

    def add_edge(self, edge: Edge) -> bool:
        """新增關係（增強版）"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 檢查節點是否存在
                cursor.execute("SELECT id FROM nodes WHERE id = ?", (edge.source,))
                if not cursor.fetchone():
                    print(f"Warning: Source node '{edge.source}' does not exist")
                    return False

                cursor.execute("SELECT id FROM nodes WHERE id = ?", (edge.target,))
                if not cursor.fetchone():
                    print(f"Warning: Target node '{edge.target}' does not exist")
                    return False

                # 自動分類 interaction_category
                if edge.interaction_type and not edge.interaction_category:
                    edge.interaction_category = self._categorize_interaction(
                        edge.interaction_type
                    )

                # 自動設定 first_seen
                if not edge.first_seen:
                    edge.first_seen = edge.date or datetime.now().strftime("%Y-%m-%d")

                cursor.execute(
                    """
                    INSERT INTO edges (source, target, type, interaction_type, interaction_category,
                                     date, description, strength, direction, verified, 
                                     evidence_count, first_seen, sentiment, attributes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        edge.source,
                        edge.target,
                        edge.type,
                        edge.interaction_type,
                        edge.interaction_category,
                        edge.date,
                        edge.description,
                        edge.strength,
                        edge.direction,
                        1 if edge.verified else 0,
                        edge.evidence_count,
                        edge.first_seen,
                        edge.sentiment,
                        json.dumps(edge.attributes, ensure_ascii=False)
                        if edge.attributes
                        else None,
                    ),
                )

                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding edge: {e}")
            return False

    def _categorize_interaction(self, interaction_type: str) -> str:
        """自動分類互動類型"""
        if not interaction_type:
            return "general"

        interaction_lower = interaction_type.lower()

        for category, types in INTERACTION_CATEGORIES.items():
            for t in types:
                if t in interaction_lower or interaction_lower in t:
                    return category

        # 預設關鍵字匹配
        if any(kw in interaction_lower for kw in ["記者會", "遊行", "抗議", "演講"]):
            return "public_action"
        elif any(kw in interaction_lower for kw in ["提案", "修法", "質詢", "連署"]):
            return "legislative"
        elif any(kw in interaction_lower for kw in ["報導", "新聞", "提及"]):
            return "media"
        elif any(kw in interaction_lower for kw in ["出庭", "作證", "代理"]):
            return "legal"
        elif any(kw in interaction_lower for kw in ["創立", "加入", "領導"]):
            return "organizational"

        return "general"

    def add_statement(
        self,
        node_id: str,
        date: str,
        occasion: str,
        content: str,
        stance_mark: int = 0,
        source_url: Optional[str] = None,
        source_media: Optional[str] = None,
    ) -> bool:
        """新增發言記錄"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO statements (node_id, date, occasion, content, 
                                          stance_mark, source_url, source_media)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        node_id,
                        date,
                        occasion,
                        content,
                        stance_mark,
                        source_url,
                        source_media,
                    ),
                )

                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding statement: {e}")
            return False

    def get_node(self, node_id: str) -> Optional[Node]:
        """取得節點資訊"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM nodes WHERE id = ?", (node_id,))
            row = cursor.fetchone()

            if row:
                return Node(
                    id=row[0],
                    name=row[1],
                    type=row[2],
                    role=row[3],
                    party=row[4],
                    stance=row[5],
                    description=row[6],
                    first_seen=row[7],
                    last_updated=row[8],
                    attributes=json.loads(row[9]) if row[9] else None,
                )
            return None

    def get_all_nodes(
        self, node_type: Optional[str] = None, stance: Optional[int] = None
    ) -> List[Node]:
        """取得所有節點（可篩選）"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            query = "SELECT * FROM nodes WHERE 1=1"
            params = []

            if node_type:
                query += " AND type = ?"
                params.append(node_type)

            if stance is not None:
                query += " AND stance = ?"
                params.append(stance)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            return [
                Node(
                    id=row[0],
                    name=row[1],
                    type=row[2],
                    role=row[3],
                    party=row[4],
                    stance=row[5],
                    description=row[6],
                    first_seen=row[7],
                    last_updated=row[8],
                    attributes=json.loads(row[9]) if row[9] else None,
                )
                for row in rows
            ]

    def get_all_edges(
        self,
        edge_type: Optional[str] = None,
        min_strength: Optional[float] = None,
        verified_only: bool = False,
        interaction_category: Optional[str] = None,
    ) -> List[Edge]:
        """取得所有邊緣關係（可篩選）

        Args:
            edge_type: 篩選特定邊緣類型
            min_strength: 最小關係強度 (0.0-1.0)
            verified_only: 只返回已驗證的關係
            interaction_category: 篩選互動類別
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            query = """
                SELECT source, target, type, interaction_type, date, description, 
                       attributes, strength, direction, verified, evidence_count, 
                       first_seen, sentiment, interaction_category
                FROM edges 
                WHERE 1=1
            """
            params = []

            if edge_type:
                query += " AND type = ?"
                params.append(edge_type)

            if min_strength is not None:
                query += " AND strength >= ?"
                params.append(min_strength)

            if verified_only:
                query += " AND verified = 1"

            if interaction_category:
                query += " AND interaction_category = ?"
                params.append(interaction_category)

            query += " ORDER BY strength DESC, first_seen DESC"

            cursor.execute(query, params)
            rows = cursor.fetchall()

            return [
                Edge(
                    source=row[0],
                    target=row[1],
                    type=row[2],
                    interaction_type=row[3],
                    date=row[4],
                    description=row[5],
                    attributes=json.loads(row[6]) if row[6] else None,
                    strength=row[7],
                    direction=row[8],
                    verified=bool(row[9]),
                    evidence_count=row[10],
                    first_seen=row[11],
                    sentiment=row[12],
                    interaction_category=row[13],
                )
                for row in rows
            ]

    def get_network(
        self, center_node: str, depth: int = 1
    ) -> Tuple[List[Node], List[Edge]]:
        """取得節點周邊網絡（BFS）"""
        nodes = set()
        edges = []
        visited = set()
        queue = [(center_node, 0)]

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            while queue:
                current_id, current_depth = queue.pop(0)

                if current_id in visited or current_depth > depth:
                    continue

                visited.add(current_id)
                nodes.add(current_id)

                # 取得相鄰節點
                cursor.execute(
                    """
                    SELECT source, target, type, interaction_type, date, description, 
                           attributes, strength, direction, verified, evidence_count, 
                           first_seen, sentiment, interaction_category
                    FROM edges 
                    WHERE source = ? OR target = ?
                """,
                    (current_id, current_id),
                )

                for row in cursor.fetchall():
                    source, target = row[0], row[1]
                    edge = Edge(
                        source=source,
                        target=target,
                        type=row[2],
                        interaction_type=row[3],
                        date=row[4],
                        description=row[5],
                        attributes=json.loads(row[6]) if row[6] else None,
                        strength=row[7],
                        direction=row[8],
                        verified=bool(row[9]),
                        evidence_count=row[10],
                        first_seen=row[11],
                        sentiment=row[12],
                        interaction_category=row[13],
                    )
                    edges.append(edge)

                    neighbor = target if source == current_id else source
                    if neighbor not in visited and current_depth < depth:
                        queue.append((neighbor, current_depth + 1))

        # 取得節點詳細資訊
        node_objects = []
        for node_id in nodes:
            node = self.get_node(node_id)
            if node:
                node_objects.append(node)

        return node_objects, edges

    def get_node_statements(
        self, node_id: str, limit: Optional[int] = None
    ) -> List[Dict]:
        """取得節點發言記錄"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            query = """
                SELECT date, occasion, content, stance_mark, source_url, source_media
                FROM statements 
                WHERE node_id = ? 
                ORDER BY date DESC
            """
            if limit:
                query += f" LIMIT {limit}"

            cursor.execute(query, (node_id,))
            rows = cursor.fetchall()

            return [
                {
                    "date": row[0],
                    "occasion": row[1],
                    "content": row[2],
                    "stance_mark": row[3],
                    "source_url": row[4],
                    "source_media": row[5],
                }
                for row in rows
            ]

    def export_to_cytoscape(self, output_path: Optional[str] = None) -> Dict:
        """匯出為 Cytoscape.js 格式（網站視覺化）"""
        nodes = self.get_all_nodes()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT source, target, type, interaction_type, date, description, 
                          strength, direction, verified, evidence_count, sentiment, interaction_category
                   FROM edges"""
            )
            edges = cursor.fetchall()

        cytoscape_data = {"nodes": [], "edges": []}

        for node in nodes:
            cytoscape_data["nodes"].append(
                {
                    "data": {
                        "id": node.id,
                        "label": node.name,
                        "type": node.type,
                        "role": node.role,
                        "party": node.party,
                        "stance": node.stance,
                        "stance_label": "⭐" * node.stance
                        if node.stance > 0
                        else "未評估",
                        "description": node.description,
                    },
                    "style": {
                        "background-color": STANCE_COLORS.get(node.stance, "#95A5A6"),
                        "shape": NODE_SHAPES.get(node.type, "ellipse"),
                    },
                }
            )

        for edge in edges:
            edge_style = {
                "line-color": EDGE_TYPE_COLORS.get(edge[2], "#999999"),
                "width": 1 + (edge[6] or 0.5) * 3,
                "line-style": "solid" if edge[8] else "dashed",
            }

            cytoscape_data["edges"].append(
                {
                    "data": {
                        "source": edge[0],
                        "target": edge[1],
                        "type": edge[2],
                        "interaction": edge[3],
                        "label": edge[3] if edge[3] else edge[2],
                        "strength": edge[6],
                        "direction": edge[7],
                        "verified": bool(edge[8]),
                        "evidence_count": edge[9],
                        "sentiment": edge[10],
                        "interaction_category": edge[11],
                    },
                    "style": edge_style,
                }
            )

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(cytoscape_data, f, ensure_ascii=False, indent=2)

        return cytoscape_data

    def export_to_d3(self, output_path: Optional[str] = None) -> Dict:
        """匯出為 D3.js 力導向圖格式"""
        nodes = self.get_all_nodes()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT source, target, type, interaction_type, strength, 
                          direction, verified, evidence_count, sentiment, interaction_category
                   FROM edges"""
            )
            edges = cursor.fetchall()

        d3_data = {
            "nodes": [
                {
                    "id": node.id,
                    "name": node.name,
                    "group": node.type,
                    "stance": node.stance,
                    "party": node.party,
                    "role": node.role,
                }
                for node in nodes
            ],
            "links": [
                {
                    "source": edge[0],
                    "target": edge[1],
                    "type": edge[2],
                    "interaction": edge[3],
                    "strength": edge[4],
                    "direction": edge[5],
                    "verified": bool(edge[6]),
                    "evidence_count": edge[7],
                    "sentiment": edge[8],
                    "interaction_category": edge[9],
                    "value": edge[4] or 0.5,
                }
                for edge in edges
            ],
        }

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(d3_data, f, ensure_ascii=False, indent=2)

        return d3_data

    def export_to_graphml(self, output_path: Optional[str] = None) -> str:
        """匯出為 GraphML 格式（通用圖形格式，Neo4j、Gephi 等支援）"""
        nodes = self.get_all_nodes()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT source, target, type, interaction_type, date, description, 
                          strength, direction, verified, evidence_count, sentiment, interaction_category
                   FROM edges"""
            )
            edges = cursor.fetchall()

        graphml = """<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <key id="d0" for="node" attr.name="name" attr.type="string"/>
  <key id="d1" for="node" attr.name="type" attr.type="string"/>
  <key id="d2" for="node" attr.name="role" attr.type="string"/>
  <key id="d3" for="node" attr.name="party" attr.type="string"/>
  <key id="d4" for="node" attr.name="stance" attr.type="int"/>
  <key id="d5" for="edge" attr.name="type" attr.type="string"/>
  <key id="d6" for="edge" attr.name="interaction" attr.type="string"/>
  <key id="d7" for="edge" attr.name="date" attr.type="string"/>
  <key id="d8" for="edge" attr.name="strength" attr.type="double"/>
  <key id="d9" for="edge" attr.name="direction" attr.type="string"/>
  <key id="d10" for="edge" attr.name="verified" attr.type="boolean"/>
  <key id="d11" for="edge" attr.name="evidence_count" attr.type="int"/>
  <key id="d12" for="edge" attr.name="sentiment" attr.type="double"/>
  <key id="d13" for="edge" attr.name="interaction_category" attr.type="string"/>
  <graph id="G" edgedefault="undirected">
"""

        for node in nodes:
            graphml += f'    <node id="{node.id}">\n'
            graphml += f'      <data key="d0">{node.name}</data>\n'
            graphml += f'      <data key="d1">{node.type}</data>\n'
            if node.role:
                graphml += f'      <data key="d2">{node.role}</data>\n'
            if node.party:
                graphml += f'      <data key="d3">{node.party}</data>\n'
            graphml += f'      <data key="d4">{node.stance}</data>\n'
            graphml += "    </node>\n"

        for i, edge in enumerate(edges):
            graphml += f'    <edge id="e{i}" source="{edge[0]}" target="{edge[1]}">\n'
            graphml += f'      <data key="d5">{edge[2]}</data>\n'
            if edge[3]:
                graphml += f'      <data key="d6">{edge[3]}</data>\n'
            if edge[4]:
                graphml += f'      <data key="d7">{edge[4]}</data>\n'
            if edge[6] is not None:
                graphml += f'      <data key="d8">{edge[6]}</data>\n'
            if edge[7]:
                graphml += f'      <data key="d9">{edge[7]}</data>\n'
            graphml += f'      <data key="d10">{bool(edge[8])}</data>\n'
            if edge[9] is not None:
                graphml += f'      <data key="d11">{edge[9]}</data>\n'
            if edge[10] is not None:
                graphml += f'      <data key="d12">{edge[10]}</data>\n'
            if edge[11]:
                graphml += f'      <data key="d13">{edge[11]}</data>\n'
            graphml += "    </edge>\n"

        graphml += "  </graph>\n</graphml>"

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(graphml)

        return graphml

    def export_to_csv(self, output_prefix: Optional[str] = None) -> Tuple[str, str]:
        """匯出為 CSV 格式（節點與關係分開）"""
        import csv

        nodes = self.get_all_nodes()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT source, target, type, interaction_type, date, description, 
                          strength, direction, verified, evidence_count, sentiment, interaction_category
                   FROM edges"""
            )
            edges = cursor.fetchall()

        # 匯出節點
        nodes_path = (
            f"{output_prefix}_nodes.csv"
            if output_prefix
            else str(EXPORT_PATH / "nodes.csv")
        )
        with open(nodes_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["id", "name", "type", "role", "party", "stance", "description"]
            )
            for node in nodes:
                writer.writerow(
                    [
                        node.id,
                        node.name,
                        node.type,
                        node.role,
                        node.party,
                        node.stance,
                        node.description,
                    ]
                )

        # 匯出關係
        edges_path = (
            f"{output_prefix}_edges.csv"
            if output_prefix
            else str(EXPORT_PATH / "edges.csv")
        )
        with open(edges_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "source",
                    "target",
                    "type",
                    "interaction_type",
                    "date",
                    "description",
                    "strength",
                    "direction",
                    "verified",
                    "evidence_count",
                    "sentiment",
                    "interaction_category",
                ]
            )
            for edge in edges:
                writer.writerow(edge)

        return nodes_path, edges_path

    def calculate_relationship_strength(
        self,
        source: str,
        target: str,
        base_strength: float = 0.5,
        evidence_count: int = 1,
        recency_days: Optional[int] = None,
    ) -> float:
        """自動計算關係強度

        基於以下因素計算:
        - 基礎強度 (base_strength): 0.0-1.0
        - 證據數量 (evidence_count): 每個證據 +0.1, 最多 +0.3
        - 時間衰減 (recency_days): 越近期越強，超過 365 天開始衰減

        最終強度範圍: 0.1 - 1.0
        """
        strength = base_strength

        # 證據加成 (每個證據 +0.1, 上限 +0.3)
        evidence_bonus = min(evidence_count * 0.1, 0.3)
        strength += evidence_bonus

        # 時間衰減 (可選)
        if recency_days is not None:
            if recency_days <= 30:
                strength += 0.1  # 近期互動加成
            elif recency_days > 365:
                decay = min((recency_days - 365) / 365 * 0.2, 0.2)
                strength -= decay

        # 確保在 0.1-1.0 範圍內
        return max(0.1, min(1.0, strength))

    def update_edge_strength(self, source: str, target: str) -> bool:
        """根據現有數據自動更新邊緣強度"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """SELECT evidence_count, first_seen 
                   FROM edges WHERE source = ? AND target = ?""",
                (source, target),
            )
            row = cursor.fetchone()

            if not row:
                return False

            evidence_count, first_seen = row

            # 計算天數
            recency_days = None
            if first_seen:
                try:
                    first_date = datetime.strptime(first_seen, "%Y-%m-%d")
                    recency_days = (datetime.now() - first_date).days
                except ValueError:
                    pass

            # 計算新強度
            new_strength = self.calculate_relationship_strength(
                source,
                target,
                base_strength=0.5,
                evidence_count=evidence_count or 1,
                recency_days=recency_days,
            )

            # 更新資料庫
            cursor.execute(
                "UPDATE edges SET strength = ? WHERE source = ? AND target = ?",
                (new_strength, source, target),
            )
            conn.commit()

            return True

    def auto_calculate_all_strengths(self) -> int:
        """自動計算所有邊緣的關係強度"""
        edges = self.get_all_edges()
        updated_count = 0

        for edge in edges:
            if self.update_edge_strength(edge.source, edge.target):
                updated_count += 1

        return updated_count

    def get_statistics(self) -> Dict:
        """取得資料庫統計資訊"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 節點統計
            cursor.execute("SELECT COUNT(*) FROM nodes")
            total_nodes = cursor.fetchone()[0]

            cursor.execute("SELECT type, COUNT(*) FROM nodes GROUP BY type")
            node_types = dict(cursor.fetchall())

            cursor.execute(
                "SELECT stance, COUNT(*) FROM nodes WHERE stance > 0 GROUP BY stance"
            )
            stance_dist = dict(cursor.fetchall())

            # 關係統計
            cursor.execute("SELECT COUNT(*) FROM edges")
            total_edges = cursor.fetchone()[0]

            cursor.execute("SELECT type, COUNT(*) FROM edges GROUP BY type")
            edge_types = dict(cursor.fetchall())

            # 發言統計
            cursor.execute("SELECT COUNT(*) FROM statements")
            total_statements = cursor.fetchone()[0]

            return {
                "total_nodes": total_nodes,
                "node_types": node_types,
                "stance_distribution": stance_dist,
                "total_edges": total_edges,
                "edge_types": edge_types,
                "total_statements": total_statements,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }


def main():
    parser = argparse.ArgumentParser(
        description="本地圖形資料庫管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # 初始化資料庫
    python graph_db.py --init
    
    # 新增人物節點
    python graph_db.py --add-node "wang_wanyu" --name "王婉諭" --type person \\
        --role "立委" --party "時代力量" --stance 5 \\
        --description "小燈泡案受害者母親，積極推動修法"
    
    # 新增組織節點
    python graph_db.py --add-node "victims_rights_assoc" --name "生命權平等協會" \\
        --type organization --stance 5
    
    # 建立關係
    python graph_db.py --add-edge "wang_wanyu" "victims_rights_assoc" \\
        --type ally --interaction "聯合記者會" --date "2024-01-15"
    
    # 新增發言記錄
    python graph_db.py --add-statement "wang_wanyu" --date "2024-01-15" \\
        --occasion "立法院質詢" --content "要求加速修法進度" --stance 5
    
    # 查詢人物網絡（深度2層）
    python graph_db.py --query-network "wang_wanyu" --depth 2
    
    # 匯出為 Cytoscape.js 格式（網站視覺化）
    python graph_db.py --export --format cytoscape --output stakeholders.json
    
    # 匯出為 GraphML（Neo4j/Gephi）
    python graph_db.py --export --format graphml --output stakeholders.graphml
    
    # 匯出為 D3.js 格式
    python graph_db.py --export --format d3 --output stakeholders_d3.json
    
    # 匯出為 CSV
    python graph_db.py --export --format csv --output stakeholders
    
    # 統計報告
    python graph_db.py --stats
        """,
    )

    parser.add_argument("--init", action="store_true", help="初始化資料庫")
    parser.add_argument("--add-node", type=str, help="新增節點（ID）")
    parser.add_argument("--name", type=str, help="節點名稱")
    parser.add_argument(
        "--type",
        type=str,
        choices=["person", "organization", "party", "official", "case"],
        help="節點類型",
    )
    parser.add_argument("--role", type=str, help="角色/職稱")
    parser.add_argument("--party", type=str, help="所屬政黨/組織")
    parser.add_argument(
        "--stance", type=int, choices=[0, 1, 2, 3, 4, 5], help="立場評分（0-5星）"
    )
    parser.add_argument("--description", type=str, help="描述")

    parser.add_argument(
        "--add-edge",
        type=str,
        nargs=2,
        metavar=("SOURCE", "TARGET"),
        help="新增關係（來源節點 目標節點）",
    )
    parser.add_argument(
        "--edge-type",
        type=str,
        choices=["ally", "oppose", "interact", "hierarchy", "family"],
        help="關係類型",
    )
    parser.add_argument("--interaction", type=str, help="互動類型（記者會、質詢等）")
    parser.add_argument("--date", type=str, help="日期（YYYY-MM-DD）")

    parser.add_argument(
        "--add-statement", type=str, metavar="NODE_ID", help="新增發言記錄（節點ID）"
    )
    parser.add_argument("--occasion", type=str, help="發言場合")
    parser.add_argument("--content", type=str, help="發言內容")
    parser.add_argument(
        "--stance-mark", type=int, choices=[1, 2, 3, 4, 5], help="發言立場標記"
    )
    parser.add_argument("--source-url", type=str, help="來源URL")
    parser.add_argument("--source-media", type=str, help="來源媒體")

    parser.add_argument(
        "--query-network",
        type=str,
        metavar="NODE_ID",
        help="查詢人物網絡（中心節點ID）",
    )
    parser.add_argument("--depth", type=int, default=1, help="網絡深度（預設1）")

    parser.add_argument("--export", action="store_true", help="匯出資料")
    parser.add_argument(
        "--format",
        type=str,
        choices=["cytoscape", "d3", "graphml", "csv"],
        help="匯出格式",
    )
    parser.add_argument("--output", type=str, help="輸出檔案路徑")

    parser.add_argument("--stats", action="store_true", help="顯示統計資訊")

    args = parser.parse_args()

    db = GraphDatabase()

    if args.init:
        print(f"✅ 資料庫已初始化：{DB_PATH}")

    elif args.add_node:
        node = Node(
            id=args.add_node,
            name=args.name or args.add_node,
            type=args.type or "person",
            role=args.role,
            party=args.party,
            stance=args.stance or 0,
            description=args.description,
        )
        if db.add_node(node):
            print(f"✅ 已新增/更新節點：{node.name} ({node.id})")
        else:
            print(f"❌ 新增節點失敗")

    elif args.add_edge:
        edge = Edge(
            source=args.add_edge[0],
            target=args.add_edge[1],
            type=args.edge_type or "interact",
            interaction_type=args.interaction,
            date=args.date,
        )
        if db.add_edge(edge):
            print(f"✅ 已新增關係：{edge.source} --{edge.type}--> {edge.target}")
        else:
            print(f"❌ 新增關係失敗")

    elif args.add_statement:
        if db.add_statement(
            args.add_statement,
            args.date,
            args.occasion,
            args.content,
            args.stance_mark or 0,
            args.source_url,
            args.source_media,
        ):
            print(f"✅ 已新增發言記錄：{args.add_statement}")
        else:
            print(f"❌ 新增發言記錄失敗")

    elif args.query_network:
        nodes, edges = db.get_network(args.query_network, args.depth)
        print(
            f"\n🌐 人物網絡查詢結果（中心：{args.query_network}，深度：{args.depth}）\n"
        )
        print(f"節點數量：{len(nodes)}")
        print(f"關係數量：{len(edges)}\n")

        print("人物清單：")
        for node in nodes:
            print(
                f"  - {node.name} ({node.type}) {'⭐' * node.stance if node.stance > 0 else ''}"
            )

        print("\n關係清單：")
        for edge in edges:
            print(f"  - {edge.source} --[{edge.type}]--> {edge.target}")

    elif args.export:
        EXPORT_PATH.mkdir(exist_ok=True)

        if args.format == "cytoscape":
            output = args.output or str(EXPORT_PATH / "stakeholders_cytoscape.json")
            db.export_to_cytoscape(output)
            print(f"✅ 已匯出為 Cytoscape.js 格式：{output}")
            print(f"   用途：網站前端視覺化（使用 Cytoscape.js 套件）")

        elif args.format == "d3":
            output = args.output or str(EXPORT_PATH / "stakeholders_d3.json")
            db.export_to_d3(output)
            print(f"✅ 已匯出為 D3.js 格式：{output}")
            print(f"   用途：網站前端視覺化（使用 D3.js 力導向圖）")

        elif args.format == "graphml":
            output = args.output or str(EXPORT_PATH / "stakeholders.graphml")
            db.export_to_graphml(output)
            print(f"✅ 已匯出為 GraphML 格式：{output}")
            print(f"   用途：匯入 Neo4j、Gephi、Cytoscape Desktop 等專業圖形工具")

        elif args.format == "csv":
            prefix = args.output or str(EXPORT_PATH / "stakeholders")
            nodes_path, edges_path = db.export_to_csv(prefix)
            print(f"✅ 已匯出為 CSV 格式：")
            print(f"   - 節點：{nodes_path}")
            print(f"   - 關係：{edges_path}")
            print(f"   用途：Excel 分析、資料庫匯入、其他工具處理")

        else:
            print("❌ 請指定匯出格式：--format [cytoscape|d3|graphml|csv]")

    elif args.stats:
        stats = db.get_statistics()
        print("\n📊 圖形資料庫統計報告\n")
        print(f"總節點數：{stats['total_nodes']}")
        print(f"總關係數：{stats['total_edges']}")
        print(f"總發言數：{stats['total_statements']}")
        print(f"最後更新：{stats['last_updated']}\n")

        print("節點類型分布：")
        for node_type, count in stats["node_types"].items():
            print(f"  - {node_type}: {count}")

        print("\n立場分布（已評估）：")
        for stance, count in sorted(stats["stance_distribution"].items(), reverse=True):
            stars = "⭐" * stance
            print(f"  - {stars} ({stance}): {count}")

        print("\n關係類型分布：")
        for edge_type, count in stats["edge_types"].items():
            print(f"  - {edge_type}: {count}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
