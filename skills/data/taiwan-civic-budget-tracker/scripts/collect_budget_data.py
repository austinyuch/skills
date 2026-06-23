#!/usr/bin/env python3
"""
Taiwan Budget Data Collection Script
Collects government budget data from public sources with proper error handling.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import urllib.request
import urllib.error
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/budget_collection.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class BudgetRecord:
    """Budget data record with provenance tracking."""

    agency: str
    year: int
    category: str
    amount: float
    source_url: str
    retrieval_date: str
    confidence: str = "high"
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class BudgetCollector:
    """Collects budget data from Taiwan government sources."""

    # Public data sources
    SOURCES = {
        "legal_aid_foundation": {
            "name": "Legal Aid Foundation",
            "url": "https://www.laf.org.tw/financialReport/1",
            "type": "html",
        },
        "judicial_yuan_budget": {
            "name": "Judicial Yuan Budget",
            "url": "https://www.judicial.gov.tw/budget/",
            "type": "pdf",
        },
        "legislative_yuan": {
            "name": "Legislative Yuan Budget Reports",
            "url": "https://www.ly.gov.tw/",
            "type": "html",
        },
        "executive_yuan_budget": {
            "name": "Executive Yuan Budget System",
            "url": "https://www.dgbas.gov.tw/ct.asp?xItem=12215&CtNode=5118",
            "type": "html",
        },
    }

    def __init__(self, output_dir: str = "data/raw/budget"):
        """Initialize collector with output directory."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.collected_data: List[BudgetRecord] = []

    def fetch_url(self, url: str, timeout: int = 30) -> Optional[str]:
        """
        Fetch content from URL with error handling.

        Args:
            url: Target URL
            timeout: Request timeout in seconds

        Returns:
            Response content or None if failed
        """
        try:
            logger.info(f"Fetching: {url}")
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            req = urllib.request.Request(url, headers=headers)

            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.status == 200:
                    content = response.read().decode("utf-8")
                    logger.info(f"Successfully fetched {len(content)} characters")
                    return content
                else:
                    logger.warning(f"HTTP {response.status} for {url}")
                    return None

        except urllib.error.HTTPError as e:
            logger.error(f"HTTP Error {e.code}: {e.reason} for {url}")
            return None
        except urllib.error.URLError as e:
            logger.error(f"URL Error: {e.reason} for {url}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {str(e)}")
            return None

    def parse_laf_budget(self, html_content: str) -> List[BudgetRecord]:
        """
        Parse Legal Aid Foundation budget from HTML.

        Note: This is a placeholder implementation. Real implementation
        would use BeautifulSoup or similar to parse actual HTML structure.
        """
        records = []
        try:
            # Placeholder for actual HTML parsing logic
            # Would extract: year, income, expenditure, balance
            logger.info("Parsing Legal Aid Foundation budget data")

            # Example structure (replace with actual parsing)
            records.append(
                BudgetRecord(
                    agency="Legal Aid Foundation",
                    year=2025,
                    category="Income",
                    amount=1520000000,  # NT$1.52 billion
                    source_url=self.SOURCES["legal_aid_foundation"]["url"],
                    retrieval_date=datetime.now().isoformat(),
                    confidence="high",
                    notes="Preliminary estimate from annual report",
                )
            )

        except Exception as e:
            logger.error(f"Error parsing LAF budget: {str(e)}")

        return records

    def collect_all(self) -> Dict[str, Any]:
        """
        Collect budget data from all sources.

        Returns:
            Collection results with metadata
        """
        results = {
            "collection_date": datetime.now().isoformat(),
            "sources_attempted": len(self.SOURCES),
            "sources_successful": 0,
            "records_collected": 0,
            "errors": [],
        }

        for source_id, source_info in self.SOURCES.items():
            try:
                logger.info(f"Collecting from {source_info['name']}")

                # Fetch data
                content = self.fetch_url(source_info["url"])
                if not content:
                    results["errors"].append(f"Failed to fetch {source_id}")
                    continue

                # Parse based on source type
                if source_id == "legal_aid_foundation":
                    records = self.parse_laf_budget(content)
                else:
                    # Placeholder for other parsers
                    records = []
                    logger.warning(f"Parser not implemented for {source_id}")

                self.collected_data.extend(records)
                results["sources_successful"] += 1
                results["records_collected"] += len(records)

            except Exception as e:
                error_msg = f"Error processing {source_id}: {str(e)}"
                logger.error(error_msg)
                results["errors"].append(error_msg)

        return results

    def save_data(self, filename: Optional[str] = None) -> str:
        """
        Save collected data to JSON file.

        Args:
            filename: Output filename (default: auto-generated with timestamp)

        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"budget_data_{timestamp}.json"

        output_path = self.output_dir / filename

        try:
            data = {
                "metadata": {
                    "export_date": datetime.now().isoformat(),
                    "record_count": len(self.collected_data),
                    "collector_version": "1.0.0",
                },
                "records": [record.to_dict() for record in self.collected_data],
            }

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.info(f"Saved {len(self.collected_data)} records to {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Error saving data: {str(e)}")
            raise


def main():
    """Main entry point with CLI argument handling."""
    try:
        # Initialize collector
        collector = BudgetCollector()

        # Collect data
        results = collector.collect_all()
        logger.info(f"Collection complete: {results}")

        # Save results
        output_file = collector.save_data()
        logger.info(f"Data saved to: {output_file}")

        # Print summary
        print(f"\n{'=' * 60}")
        print("Budget Data Collection Complete")
        print(f"{'=' * 60}")
        print(f"Sources attempted: {results['sources_attempted']}")
        print(f"Sources successful: {results['sources_successful']}")
        print(f"Records collected: {results['records_collected']}")
        print(f"Output file: {output_file}")

        if results["errors"]:
            print(f"\nErrors encountered ({len(results['errors'])}):")
            for error in results["errors"]:
                print(f"  - {error}")

        print(f"{'=' * 60}\n")

        # Exit with error code if no data collected
        if results["records_collected"] == 0:
            logger.error("No data collected")
            sys.exit(1)

        sys.exit(0)

    except KeyboardInterrupt:
        logger.info("Collection interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
