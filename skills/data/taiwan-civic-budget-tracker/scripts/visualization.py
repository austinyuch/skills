#!/usr/bin/env python3
"""
Visualization Script
Generates charts and network visualizations for budget and procurement data.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/visualization.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class BudgetVisualizer:
    """Creates visualizations for budget and procurement data."""

    def __init__(self, output_dir: str = "data/reports/charts"):
        """Initialize with output directory."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_budget_data(self, filepath: str) -> List[Dict]:
        """Load budget data from JSON file."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                records = data.get("records", [])
                logger.info(f"Loaded {len(records)} budget records")
                return records
        except Exception as e:
            logger.error(f"Error loading budget data: {str(e)}")
            return []

    def generate_budget_summary_text(self, records: List[Dict]) -> str:
        """
        Generate a text-based budget summary report.

        Args:
            records: List of budget records

        Returns:
            Formatted text report
        """
        if not records:
            return "No budget records available."

        # Aggregate by year and category
        summary = {}
        for record in records:
            year = record.get("year", "Unknown")
            category = record.get("category", "Other")
            amount = record.get("amount", 0)

            if year not in summary:
                summary[year] = {}
            if category not in summary[year]:
                summary[year][category] = 0

            summary[year][category] += amount

        # Generate report
        lines = [
            "=" * 60,
            "BUDGET SUMMARY REPORT",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 60,
            "",
        ]

        for year in sorted(summary.keys()):
            lines.append(f"Year: {year}")
            lines.append("-" * 40)

            total = 0
            for category, amount in sorted(summary[year].items()):
                lines.append(f"  {category:<30} NT${amount:>15,.0f}")
                total += amount

            lines.append("-" * 40)
            lines.append(f"  {'TOTAL':<30} NT${total:>15,.0f}")
            lines.append("")

        lines.append("=" * 60)

        return "\n".join(lines)

    def generate_procurement_summary_text(self, records: List[Dict]) -> str:
        """
        Generate a text-based procurement summary report.

        Args:
            records: List of procurement records

        Returns:
            Formatted text report
        """
        if not records:
            return "No procurement records available."

        # Calculate statistics
        total_records = len(records)
        awarded_records = [r for r in records if r.get("award_amount")]
        total_award_amount = sum(r.get("award_amount", 0) for r in awarded_records)

        # Count by agency
        agency_counts = {}
        agency_amounts = {}
        for record in records:
            agency = record.get("agency", "Unknown")
            agency_counts[agency] = agency_counts.get(agency, 0) + 1

            amount = record.get("award_amount", 0)
            agency_amounts[agency] = agency_amounts.get(agency, 0) + amount

        # Count by vendor
        vendor_counts = {}
        for record in records:
            vendor = record.get("vendor_name")
            if vendor:
                vendor_counts[vendor] = vendor_counts.get(vendor, 0) + 1

        # Generate report
        lines = [
            "=" * 70,
            "PROCUREMENT SUMMARY REPORT",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 70,
            "",
            f"Total Records: {total_records}",
            f"Awarded Cases: {len(awarded_records)}",
            f"Total Award Amount: NT${total_award_amount:,.0f}",
            "",
            "TOP 10 AGENCIES BY CASE COUNT",
            "-" * 70,
        ]

        sorted_agencies = sorted(
            agency_counts.items(), key=lambda x: x[1], reverse=True
        )[:10]
        for i, (agency, count) in enumerate(sorted_agencies, 1):
            amount = agency_amounts.get(agency, 0)
            lines.append(
                f"{i:2}. {agency[:40]:<40} {count:>5} cases  NT${amount:>12,.0f}"
            )

        lines.extend(["", "TOP 10 VENDORS BY CASE COUNT", "-" * 70])

        sorted_vendors = sorted(
            vendor_counts.items(), key=lambda x: x[1], reverse=True
        )[:10]
        for i, (vendor, count) in enumerate(sorted_vendors, 1):
            lines.append(f"{i:2}. {vendor[:50]:<50} {count:>5} cases")

        lines.append("=" * 70)

        return "\n".join(lines)

    def export_d3_network_json(
        self,
        entities_path: str,
        relationships_path: str,
        output_path: Optional[str] = None,
    ) -> str:
        """
        Export network data in D3.js compatible format.

        Args:
            entities_path: Path to entities JSON
            relationships_path: Path to relationships JSON
            output_path: Output file path (auto-generated if None)

        Returns:
            Path to exported file
        """
        try:
            # Load entities
            with open(entities_path, "r", encoding="utf-8") as f:
                entities_data = json.load(f)
                entities = entities_data.get("entities", [])

            # Load relationships
            with open(relationships_path, "r", encoding="utf-8") as f:
                rel_data = json.load(f)
                relationships = rel_data.get("relationships", [])

            # Convert to D3 format
            nodes = []
            for entity in entities:
                nodes.append(
                    {
                        "id": entity["id"],
                        "name": entity["name"],
                        "group": entity["type"],
                        "attributes": entity.get("attributes", {}),
                    }
                )

            links = []
            for rel in relationships:
                links.append(
                    {
                        "source": rel["source_id"],
                        "target": rel["target_id"],
                        "type": rel["type"],
                        "value": rel["attributes"].get("amount", 1),
                    }
                )

            # Create D3 data structure
            d3_data = {
                "metadata": {
                    "export_date": datetime.now().isoformat(),
                    "nodes": len(nodes),
                    "links": len(links),
                },
                "nodes": nodes,
                "links": links,
            }

            # Save
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = self.output_dir / f"network_d3_{timestamp}.json"

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(d3_data, f, ensure_ascii=False, indent=2)

            logger.info(f"Exported D3 network to {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Error exporting D3 network: {str(e)}")
            raise


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate visualizations")
    parser.add_argument("--budget", "-b", help="Budget data JSON file")
    parser.add_argument("--procurement", "-p", help="Procurement data JSON file")
    parser.add_argument("--entities", "-e", help="Entities JSON file")
    parser.add_argument("--relationships", "-r", help="Relationships JSON file")
    parser.add_argument(
        "--output", "-o", default="data/reports/charts", help="Output directory"
    )

    args = parser.parse_args()

    try:
        visualizer = BudgetVisualizer(output_dir=args.output)

        # Budget summary
        if args.budget:
            records = visualizer.load_budget_data(args.budget)
            if records:
                report = visualizer.generate_budget_summary_text(records)
                print(report)

                # Save to file
                report_path = Path(args.output) / "budget_summary.txt"
                report_path.parent.mkdir(parents=True, exist_ok=True)
                with open(report_path, "w", encoding="utf-8") as f:
                    f.write(report)
                logger.info(f"Budget summary saved to {report_path}")

        # Procurement summary
        if args.procurement:
            records = visualizer.load_budget_data(args.procurement)
            if records:
                report = visualizer.generate_procurement_summary_text(records)
                print(report)

                # Save to file
                report_path = Path(args.output) / "procurement_summary.txt"
                with open(report_path, "w", encoding="utf-8") as f:
                    f.write(report)
                logger.info(f"Procurement summary saved to {report_path}")

        # D3 network export
        if args.entities and args.relationships:
            d3_path = visualizer.export_d3_network_json(
                args.entities, args.relationships
            )
            print(f"\nD3 network exported to: {d3_path}")

        sys.exit(0)

    except KeyboardInterrupt:
        logger.info("Visualization interrupted")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
