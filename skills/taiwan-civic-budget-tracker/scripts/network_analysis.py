#!/usr/bin/env python3
"""
Network Analysis Script
Analyzes relationships between companies, agencies, and legal professionals.
"""

import json
import logging
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/network_analysis.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class Entity:
    """Generic entity node in the network."""

    id: str
    name: str
    type: str  # agency, vendor, person, case
    attributes: Dict[str, Any]
    source_url: str
    confidence: str = "high"


@dataclass
class Relationship:
    """Relationship edge between entities."""

    source_id: str
    target_id: str
    type: str  # awarded_to, employs, represented_by, etc.
    attributes: Dict[str, Any]
    source_url: str
    confidence: str = "high"


class NetworkAnalyzer:
    """Analyzes procurement and budget networks."""

    def __init__(self, data_dir: str = "data"):
        """Initialize with data directory path."""
        self.data_dir = Path(data_dir)
        self.entities: Dict[str, Entity] = {}
        self.relationships: List[Relationship] = []

    def load_procurement_data(self, filepath: str) -> List[Dict]:
        """
        Load procurement data from JSON file.

        Args:
            filepath: Path to procurement JSON file

        Returns:
            List of procurement records
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                records = data.get("records", [])
                logger.info(
                    f"Loaded {len(records)} procurement records from {filepath}"
                )
                return records
        except FileNotFoundError:
            logger.error(f"File not found: {filepath}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {filepath}: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error loading {filepath}: {str(e)}")
            return []

    def build_network(self, procurement_records: List[Dict]) -> Dict[str, Any]:
        """
        Build network graph from procurement records.

        Args:
            procurement_records: List of procurement data records

        Returns:
            Network statistics and structure
        """
        logger.info("Building network from procurement data")

        # Clear existing data
        self.entities.clear()
        self.relationships.clear()

        # Track statistics
        stats = {
            "total_records": len(procurement_records),
            "agencies": set(),
            "vendors": set(),
            "awards": 0,
            "errors": 0,
        }

        for record in procurement_records:
            try:
                # Create agency entity
                agency_id = (
                    f"agency_{record.get('agency', 'unknown').replace(' ', '_')}"
                )
                if agency_id not in self.entities:
                    self.entities[agency_id] = Entity(
                        id=agency_id,
                        name=record.get("agency", "Unknown"),
                        type="agency",
                        attributes={},
                        source_url=record.get("source_url", ""),
                        confidence=record.get("confidence", "medium"),
                    )
                    stats["agencies"].add(agency_id)

                # Create vendor entity if exists
                vendor_name = record.get("vendor_name")
                if vendor_name:
                    vendor_id = f"vendor_{vendor_name.replace(' ', '_')}"
                    if vendor_id not in self.entities:
                        self.entities[vendor_id] = Entity(
                            id=vendor_id,
                            name=vendor_name,
                            type="vendor",
                            attributes={
                                "vendor_id": record.get("vendor_id"),
                                "case_count": 0,
                                "total_award_amount": 0,
                            },
                            source_url=record.get("source_url", ""),
                            confidence=record.get("confidence", "medium"),
                        )
                        stats["vendors"].add(vendor_id)

                    # Update vendor stats
                    vendor = self.entities[vendor_id]
                    vendor.attributes["case_count"] += 1
                    award_amount = record.get("award_amount")
                    if award_amount:
                        vendor.attributes["total_award_amount"] += award_amount

                    # Create awarded_to relationship
                    self.relationships.append(
                        Relationship(
                            source_id=agency_id,
                            target_id=vendor_id,
                            type="awarded_to",
                            attributes={
                                "case_id": record.get("case_id"),
                                "case_name": record.get("case_name"),
                                "amount": award_amount,
                                "date": record.get("award_date"),
                            },
                            source_url=record.get("source_url", ""),
                            confidence=record.get("confidence", "medium"),
                        )
                    )
                    stats["awards"] += 1

            except Exception as e:
                logger.warning(f"Error processing record: {str(e)}")
                stats["errors"] += 1
                continue

        logger.info(
            f"Network built: {len(self.entities)} entities, {len(self.relationships)} relationships"
        )

        return {
            "entities": len(self.entities),
            "relationships": len(self.relationships),
            "agencies": len(stats["agencies"]),
            "vendors": len(stats["vendors"]),
            "awards": stats["awards"],
            "errors": stats["errors"],
        }

    def analyze_vendor_concentration(self) -> List[Dict]:
        """
        Analyze vendor concentration (which vendors get most awards).

        Returns:
            List of vendor analysis results
        """
        # Initialize vendor statistics dictionary with proper typing
        vendor_stats: Dict[str, Dict[str, Any]] = {}

        for rel in self.relationships:
            if rel.type == "awarded_to":
                vendor_id = rel.target_id

                # Initialize vendor entry if not exists
                if vendor_id not in vendor_stats:
                    vendor_stats[vendor_id] = {
                        "name": self.entities[vendor_id].name,
                        "case_count": 0,
                        "agencies": set(),
                        "total_amount": 0.0,
                        "cases": [],
                    }

                # Update case count
                current_count = vendor_stats[vendor_id].get("case_count", 0)
                vendor_stats[vendor_id]["case_count"] = current_count + 1

                # Add agency
                vendor_stats[vendor_id]["agencies"].add(rel.source_id)

                # Add amount
                amount = rel.attributes.get("amount")
                if amount:
                    current_amount = vendor_stats[vendor_id].get("total_amount", 0.0)
                    vendor_stats[vendor_id]["total_amount"] = current_amount + float(
                        amount
                    )

                # Add case details
                case_list = vendor_stats[vendor_id].get("cases", [])
                case_list.append(
                    {
                        "case_id": rel.attributes.get("case_id"),
                        "case_name": rel.attributes.get("case_name"),
                        "amount": amount,
                        "date": rel.attributes.get("date"),
                    }
                )
                vendor_stats[vendor_id]["cases"] = case_list

        # Convert to sorted list
        results = []
        for vendor_id, stats in vendor_stats.items():
            results.append(
                {
                    "vendor_id": vendor_id,
                    "vendor_name": stats["name"],
                    "case_count": stats["case_count"],
                    "agency_count": len(stats["agencies"]),
                    "total_amount": stats["total_amount"],
                    "cases": stats["cases"],
                }
            )

        # Sort by case count descending
        results.sort(key=lambda x: x["case_count"], reverse=True)

        logger.info(f"Analyzed {len(results)} vendors")
        return results

    def detect_anomalies(self) -> List[Dict]:
        """
        Detect anomalies in procurement patterns.

        Returns:
            List of detected anomalies
        """
        anomalies = []

        # Check 1: Vendors with unusually high award counts
        vendor_stats = self.analyze_vendor_concentration()
        if vendor_stats:
            avg_cases = sum(v["case_count"] for v in vendor_stats) / len(vendor_stats)
            threshold = avg_cases * 3  # 3x average

            for vendor in vendor_stats:
                if vendor["case_count"] > threshold:
                    anomalies.append(
                        {
                            "type": "high_volume_vendor",
                            "severity": "medium",
                            "entity": vendor["vendor_name"],
                            "details": f"Vendor has {vendor['case_count']} cases (avg: {avg_cases:.1f})",
                            "cases": vendor["cases"],
                        }
                    )

        # Check 2: Rapid successive awards to same vendor
        vendor_award_dates = defaultdict(list)
        for rel in self.relationships:
            if rel.type == "awarded_to":
                date_str = rel.attributes.get("date")
                if date_str:
                    vendor_award_dates[rel.target_id].append(date_str)

        for vendor_id, dates in vendor_award_dates.items():
            if len(dates) >= 3:
                # Check for awards within short time window
                from datetime import datetime

                try:
                    parsed_dates = sorted(
                        [datetime.strptime(d, "%Y-%m-%d") for d in dates if d]
                    )
                    for i in range(len(parsed_dates) - 2):
                        window = (parsed_dates[i + 2] - parsed_dates[i]).days
                        if window <= 30:  # 3 awards within 30 days
                            vendor_name = self.entities[vendor_id].name
                            anomalies.append(
                                {
                                    "type": "rapid_awards",
                                    "severity": "high",
                                    "entity": vendor_name,
                                    "details": f"3+ awards within {window} days",
                                    "dates": [
                                        d.strftime("%Y-%m-%d")
                                        for d in parsed_dates[i : i + 3]
                                    ],
                                }
                            )
                            break
                except Exception:
                    continue

        logger.info(f"Detected {len(anomalies)} anomalies")
        return anomalies

    def save_network(self, output_path: Optional[str] = None) -> str:
        """
        Save network data to JSON files.

        Args:
            output_path: Base output path (default: auto-generated)

        Returns:
            Path to entities file
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"data/processed/network_{timestamp}"

        output_base = Path(output_path)
        output_base.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Save entities
            entities_path = f"{output_path}_entities.json"
            entities_data = {
                "metadata": {
                    "export_date": datetime.now().isoformat(),
                    "entity_count": len(self.entities),
                },
                "entities": [asdict(e) for e in self.entities.values()],
            }

            with open(entities_path, "w", encoding="utf-8") as f:
                json.dump(entities_data, f, ensure_ascii=False, indent=2)

            # Save relationships
            relationships_path = f"{output_path}_relationships.json"
            relationships_data = {
                "metadata": {
                    "export_date": datetime.now().isoformat(),
                    "relationship_count": len(self.relationships),
                },
                "relationships": [asdict(r) for r in self.relationships],
            }

            with open(relationships_path, "w", encoding="utf-8") as f:
                json.dump(relationships_data, f, ensure_ascii=False, indent=2)

            logger.info(f"Network saved: {entities_path}, {relationships_path}")
            return entities_path

        except Exception as e:
            logger.error(f"Error saving network: {str(e)}")
            raise


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Analyze procurement network")
    parser.add_argument("input", help="Input procurement JSON file")
    parser.add_argument(
        "--output", "-o", default="data/processed", help="Output directory"
    )

    args = parser.parse_args()

    try:
        # Initialize analyzer
        analyzer = NetworkAnalyzer()

        # Load data
        records = analyzer.load_procurement_data(args.input)
        if not records:
            logger.error("No records loaded")
            sys.exit(1)

        # Build network
        stats = analyzer.build_network(records)
        print(f"\n{'=' * 60}")
        print("Network Analysis Results")
        print(f"{'=' * 60}")
        print(f"Entities: {stats['entities']}")
        print(f"Relationships: {stats['relationships']}")
        print(f"Agencies: {stats['agencies']}")
        print(f"Vendors: {stats['vendors']}")

        # Vendor concentration analysis
        print(f"\n{'=' * 60}")
        print("Top 10 Vendors by Award Count")
        print(f"{'=' * 60}")
        vendors = analyzer.analyze_vendor_concentration()[:10]
        for i, v in enumerate(vendors, 1):
            amount_str = f"NT${v['total_amount']:,.0f}" if v["total_amount"] else "N/A"
            print(f"{i}. {v['vendor_name']}")
            print(
                f"   Cases: {v['case_count']} | Agencies: {v['agency_count']} | Amount: {amount_str}"
            )

        # Anomaly detection
        anomalies = analyzer.detect_anomalies()
        if anomalies:
            print(f"\n{'=' * 60}")
            print(f"Detected Anomalies ({len(anomalies)})")
            print(f"{'=' * 60}")
            for a in anomalies:
                print(f"[{a['severity'].upper()}] {a['type']}: {a['entity']}")
                print(f"   {a['details']}")

        # Save network
        output_file = analyzer.save_network()
        print(f"\nNetwork data saved to: {output_file}")
        print(f"{'=' * 60}\n")

        sys.exit(0)

    except KeyboardInterrupt:
        logger.info("Analysis interrupted")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
