#!/usr/bin/env python3
"""
Neo4j Graph Database Integration
Stores and queries budget/procurement entities as a knowledge graph.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

try:
    from neo4j import GraphDatabase, Driver, Session

    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    print("Warning: neo4j package not installed. Run: pip install neo4j")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/neo4j_operations.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class Neo4jGraphStore:
    """
    Neo4j graph database interface for budget tracker data.

    Schema:
    - Nodes: Agency, Vendor, Case, Person, Budget, Procurement
    - Relationships: AWARDED_TO, BELONGS_TO, REPRESENTED_BY, FUNDED_BY
    """

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        user: str = "neo4j",
        password: str = "password",
    ):
        """
        Initialize Neo4j connection.

        Args:
            uri: Neo4j connection URI
            user: Database username
            password: Database password
        """
        if not NEO4J_AVAILABLE:
            raise ImportError("neo4j package required. Install with: pip install neo4j")

        self.uri = uri
        self.user = user
        self.password = password
        self.driver: Optional[Driver] = None

        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            logger.info(f"Connected to Neo4j at {uri}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    def close(self):
        """Close database connection."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")

    def init_schema(self) -> bool:
        """
        Initialize database schema with constraints and indexes.

        Returns:
            True if successful, False otherwise
        """
        if not self.driver:
            logger.error("Database driver not initialized")
            return False

        try:
            with self.driver.session() as session:
                # Create constraints for unique IDs
                constraints = [
                    "CREATE CONSTRAINT agency_id IF NOT EXISTS FOR (a:Agency) REQUIRE a.id IS UNIQUE",
                    "CREATE CONSTRAINT vendor_id IF NOT EXISTS FOR (v:Vendor) REQUIRE v.id IS UNIQUE",
                    "CREATE CONSTRAINT case_id IF NOT EXISTS FOR (c:Case) REQUIRE c.id IS UNIQUE",
                    "CREATE CONSTRAINT person_id IF NOT EXISTS FOR (p:Person) REQUIRE p.id IS UNIQUE",
                ]

                for constraint in constraints:
                    try:
                        session.run(constraint)
                        logger.info(f"Created constraint: {constraint}")
                    except Exception as e:
                        logger.warning(
                            f"Constraint creation failed (may already exist): {e}"
                        )

                # Create indexes for performance
                indexes = [
                    "CREATE INDEX agency_name IF NOT EXISTS FOR (a:Agency) ON (a.name)",
                    "CREATE INDEX vendor_name IF NOT EXISTS FOR (v:Vendor) ON (v.name)",
                    "CREATE INDEX case_name IF NOT EXISTS FOR (c:Case) ON (c.name)",
                    "CREATE INDEX entity_type IF NOT EXISTS FOR (e:Entity) ON (e.type)",
                ]

                for index in indexes:
                    try:
                        session.run(index)
                        logger.info(f"Created index: {index}")
                    except Exception as e:
                        logger.warning(f"Index creation failed: {e}")

                return True

        except Exception as e:
            logger.error(f"Error initializing schema: {e}")
            return False

    def create_agency(
        self, agency_id: str, name: str, attributes: Optional[Dict] = None
    ) -> bool:
        """
        Create an Agency node.

        Args:
            agency_id: Unique agency identifier
            name: Agency name
            attributes: Optional additional attributes

        Returns:
            True if created successfully
        """
        if not self.driver:
            return False

        try:
            with self.driver.session() as session:
                query = """
                MERGE (a:Agency {id: $id})
                SET a.name = $name,
                    a.created_at = datetime(),
                    a.attributes = $attrs
                RETURN a
                """
                session.run(
                    query, id=agency_id, name=name, attrs=json.dumps(attributes or {})
                )
                logger.debug(f"Created/updated agency: {name}")
                return True
        except Exception as e:
            logger.error(f"Error creating agency {name}: {e}")
            return False

    def create_vendor(
        self,
        vendor_id: str,
        name: str,
        vendor_reg_id: Optional[str] = None,
        attributes: Optional[Dict] = None,
    ) -> bool:
        """
        Create a Vendor node.

        Args:
            vendor_id: Unique vendor identifier
            name: Vendor name
            vendor_reg_id: Official registration number (UBNo)
            attributes: Optional additional attributes

        Returns:
            True if created successfully
        """
        if not self.driver:
            return False

        try:
            with self.driver.session() as session:
                query = """
                MERGE (v:Vendor {id: $id})
                SET v.name = $name,
                    v.vendor_reg_id = $reg_id,
                    v.created_at = datetime(),
                    v.attributes = $attrs
                RETURN v
                """
                session.run(
                    query,
                    id=vendor_id,
                    name=name,
                    reg_id=vendor_reg_id,
                    attrs=json.dumps(attributes or {}),
                )
                logger.debug(f"Created/updated vendor: {name}")
                return True
        except Exception as e:
            logger.error(f"Error creating vendor {name}: {e}")
            return False

    def create_case(
        self,
        case_id: str,
        name: str,
        case_type: str = "procurement",
        attributes: Optional[Dict] = None,
    ) -> bool:
        """
        Create a Case node (procurement or legal case).

        Args:
            case_id: Unique case identifier
            name: Case name
            case_type: Type of case (procurement, legal, etc.)
            attributes: Optional additional attributes

        Returns:
            True if created successfully
        """
        if not self.driver:
            return False

        try:
            with self.driver.session() as session:
                query = """
                MERGE (c:Case {id: $id})
                SET c.name = $name,
                    c.case_type = $case_type,
                    c.created_at = datetime(),
                    c.attributes = $attrs
                RETURN c
                """
                session.run(
                    query,
                    id=case_id,
                    name=name,
                    case_type=case_type,
                    attrs=json.dumps(attributes or {}),
                )
                logger.debug(f"Created/updated case: {name}")
                return True
        except Exception as e:
            logger.error(f"Error creating case {name}: {e}")
            return False

    def create_person(
        self,
        person_id: str,
        name: str,
        birth_year: Optional[int] = None,
        role: Optional[str] = None,
        attributes: Optional[Dict] = None,
    ) -> bool:
        """
        Create a Person node (lawyer, judge, etc.).

        Args:
            person_id: Unique person identifier
            name: Person name
            birth_year: Birth year for disambiguation
            role: Professional role (lawyer, judge, etc.)
            attributes: Optional additional attributes

        Returns:
            True if created successfully
        """
        if not self.driver:
            return False

        try:
            with self.driver.session() as session:
                query = """
                MERGE (p:Person {id: $id})
                SET p.name = $name,
                    p.birth_year = $birth_year,
                    p.role = $role,
                    p.created_at = datetime(),
                    p.attributes = $attrs
                RETURN p
                """
                session.run(
                    query,
                    id=person_id,
                    name=name,
                    birth_year=birth_year,
                    role=role,
                    attrs=json.dumps(attributes or {}),
                )
                logger.debug(f"Created/updated person: {name}")
                return True
        except Exception as e:
            logger.error(f"Error creating person {name}: {e}")
            return False

    def create_relationship(
        self, from_id: str, to_id: str, rel_type: str, attributes: Optional[Dict] = None
    ) -> bool:
        """
        Create a relationship between two nodes.

        Args:
            from_id: Source node ID
            to_id: Target node ID
            rel_type: Relationship type (e.g., 'AWARDED_TO', 'REPRESENTED_BY')
            attributes: Optional relationship attributes

        Returns:
            True if created successfully
        """
        if not self.driver:
            return False

        try:
            with self.driver.session() as session:
                query = f"""
                MATCH (a) WHERE a.id = $from_id
                MATCH (b) WHERE b.id = $to_id
                MERGE (a)-[r:{rel_type}]->(b)
                SET r.created_at = datetime(),
                    r.attributes = $attrs
                RETURN r
                """
                session.run(
                    query,
                    from_id=from_id,
                    to_id=to_id,
                    attrs=json.dumps(attributes or {}),
                )
                logger.debug(f"Created relationship: {from_id} -{rel_type}-> {to_id}")
                return True
        except Exception as e:
            logger.error(f"Error creating relationship: {e}")
            return False

    def import_procurement_network(
        self, entities: List[Dict], relationships: List[Dict]
    ) -> Dict[str, int]:
        """
        Import entire procurement network into Neo4j.

        Args:
            entities: List of entity dictionaries
            relationships: List of relationship dictionaries

        Returns:
            Import statistics
        """
        stats = {"entities": 0, "relationships": 0, "errors": 0}

        # Import entities
        for entity in entities:
            try:
                entity_type = entity.get("type", "unknown")
                entity_id = entity.get("id", "")
                name = entity.get("name", "")
                attrs = entity.get("attributes", {})

                if entity_type == "agency":
                    if self.create_agency(entity_id, name, attrs):
                        stats["entities"] += 1
                elif entity_type == "vendor":
                    vendor_reg = attrs.get("vendor_id")
                    if self.create_vendor(entity_id, name, vendor_reg, attrs):
                        stats["entities"] += 1
                elif entity_type == "case":
                    if self.create_case(entity_id, name, "procurement", attrs):
                        stats["entities"] += 1
                else:
                    logger.warning(f"Unknown entity type: {entity_type}")

            except Exception as e:
                logger.error(f"Error importing entity: {e}")
                stats["errors"] += 1

        # Import relationships
        for rel in relationships:
            try:
                source_id = rel.get("source_id")
                target_id = rel.get("target_id")
                rel_type = rel.get("type", "RELATED_TO").upper()
                attrs = rel.get("attributes", {})

                if self.create_relationship(source_id, target_id, rel_type, attrs):
                    stats["relationships"] += 1

            except Exception as e:
                logger.error(f"Error importing relationship: {e}")
                stats["errors"] += 1

        logger.info(f"Import complete: {stats}")
        return stats

    def query_vendor_network(
        self, vendor_id: Optional[str] = None, min_awards: int = 1
    ) -> List[Dict]:
        """
        Query vendor network with award counts.

        Args:
            vendor_id: Optional specific vendor to query
            min_awards: Minimum number of awards to include

        Returns:
            List of vendor network data
        """
        if not self.driver:
            return []

        try:
            with self.driver.session() as session:
                if vendor_id:
                    query = """
                    MATCH (v:Vendor {id: $vendor_id})<-[r:AWARDED_TO]-(c:Case)-[:BELONGS_TO]->(a:Agency)
                    RETURN v.name as vendor, 
                           count(r) as award_count,
                           collect(DISTINCT a.name) as agencies,
                           sum(r.attributes.amount) as total_amount
                    """
                    result = session.run(query, vendor_id=vendor_id)
                else:
                    query = """
                    MATCH (v:Vendor)<-[r:AWARDED_TO]-(c:Case)-[:BELONGS_TO]->(a:Agency)
                    WITH v, count(r) as award_count, 
                         collect(DISTINCT a.name) as agencies,
                         sum(r.attributes.amount) as total_amount
                    WHERE award_count >= $min_awards
                    RETURN v.name as vendor, award_count, agencies, total_amount
                    ORDER BY award_count DESC
                    """
                    result = session.run(query, min_awards=min_awards)

                return [dict(record) for record in result]

        except Exception as e:
            logger.error(f"Error querying vendor network: {e}")
            return []

    def find_connection_paths(
        self, from_entity: str, to_entity: str, max_depth: int = 4
    ) -> List[List[Dict]]:
        """
        Find all connection paths between two entities.

        Args:
            from_entity: Starting entity ID
            to_entity: Target entity ID
            max_depth: Maximum path depth to search

        Returns:
            List of paths, each containing node and relationship info
        """
        if not self.driver:
            return []

        try:
            with self.driver.session() as session:
                query = (
                    """
                MATCH path = (start {id: $from_id})-[:AWARDED_TO|BELONGS_TO|REPRESENTED_BY*1..%d]-(end {id: $to_id})
                RETURN [node in nodes(path) | {id: node.id, name: node.name, type: labels(node)[0]}] as nodes,
                       [rel in relationships(path) | {type: type(rel), attrs: rel.attributes}] as relationships
                LIMIT 10
                """
                    % max_depth
                )

                result = session.run(query, from_id=from_entity, to_id=to_entity)
                paths = []
                for record in result:
                    path_data = {
                        "nodes": record["nodes"],
                        "relationships": record["relationships"],
                    }
                    paths.append(path_data)

                return paths

        except Exception as e:
            logger.error(f"Error finding paths: {e}")
            return []


def main():
    """CLI for Neo4j operations."""
    import argparse

    parser = argparse.ArgumentParser(description="Neo4j graph database operations")
    parser.add_argument("--uri", default="bolt://localhost:7687", help="Neo4j URI")
    parser.add_argument("--user", default="neo4j", help="Username")
    parser.add_argument("--password", default="password", help="Password")
    parser.add_argument("--init", action="store_true", help="Initialize schema")
    parser.add_argument("--import-entities", help="Import entities JSON file")
    parser.add_argument("--import-relationships", help="Import relationships JSON file")
    parser.add_argument(
        "--query-vendors", action="store_true", help="Query vendor network"
    )

    args = parser.parse_args()

    try:
        store = Neo4jGraphStore(args.uri, args.user, args.password)

        if args.init:
            if store.init_schema():
                print("✅ Schema initialized successfully")
            else:
                print("❌ Schema initialization failed")

        if args.import_entities and args.import_relationships:
            with open(args.import_entities, "r") as f:
                entities = json.load(f).get("entities", [])
            with open(args.import_relationships, "r") as f:
                relationships = json.load(f).get("relationships", [])

            stats = store.import_procurement_network(entities, relationships)
            print(f"\n📊 Import Statistics:")
            print(f"  Entities: {stats['entities']}")
            print(f"  Relationships: {stats['relationships']}")
            print(f"  Errors: {stats['errors']}")

        if args.query_vendors:
            vendors = store.query_vendor_network(min_awards=3)
            print(f"\n🏢 Vendors with 3+ awards:")
            for v in vendors[:10]:
                print(
                    f"  {v['vendor']}: {v['award_count']} awards from {len(v['agencies'])} agencies"
                )

        store.close()

    except Exception as e:
        logger.error(f"Neo4j operation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
