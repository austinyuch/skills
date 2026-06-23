#!/usr/bin/env python3
"""
Taiwan Procurement Data Collection Script
Collects public procurement data from PCC (Public Construction Commission)
with robust error handling and anti-detection measures.
"""

import csv
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import urllib.request
import urllib.error
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/procurement_collection.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class ProcurementRecord:
    """Procurement record with full provenance tracking."""

    case_id: str
    case_name: str
    agency: str
    publish_date: str
    award_date: Optional[str]
    budget_amount: Optional[float]
    award_amount: Optional[float]
    vendor_name: Optional[str]
    vendor_id: Optional[str]  # Unified Business Number
    status: str
    category: str
    source_url: str
    retrieval_date: str
    confidence: str = "high"
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PCCScraper:
    """
    Scraper for Public Construction Commission procurement data.

    Data source: https://web.pcc.gov.tw/pis/openData/awardCSV
    CSV format includes: case_id, case_name, agency, publish_date,
    award_date, budget_amount, award_amount, vendor_name, vendor_id, etc.
    """

    BASE_URL = "https://web.pcc.gov.tw/pis/openData/awardCSV"

    def __init__(self, output_dir: str = "data/raw/pcc", delay: float = 1.0):
        """
        Initialize PCC scraper.

        Args:
            output_dir: Directory to save collected data
            delay: Delay between requests in seconds (be nice to servers)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.delay = delay
        self.collected_records: List[ProcurementRecord] = []
        self.session_cookies: Optional[str] = None

    def fetch_csv_data(self, date_from: str, date_to: str) -> Optional[str]:
        """
        Fetch CSV data from PCC open data API.

        Args:
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)

        Returns:
            CSV content as string or None if failed
        """
        try:
            # Build URL with date parameters
            params = f"?dateFrom={date_from}&dateTo={date_to}"
            url = f"{self.BASE_URL}{params}"

            logger.info(f"Fetching PCC data: {date_from} to {date_to}")

            # Set headers to mimic browser
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/csv,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }

            # Add session cookies if available
            if self.session_cookies:
                headers["Cookie"] = self.session_cookies

            req = urllib.request.Request(url, headers=headers)

            with urllib.request.urlopen(req, timeout=60) as response:
                if response.status == 200:
                    # Store cookies for next request
                    if "Set-Cookie" in response.headers:
                        self.session_cookies = response.headers["Set-Cookie"]

                    content = response.read()

                    # Handle gzip encoding
                    if response.headers.get("Content-Encoding") == "gzip":
                        import gzip

                        content = gzip.decompress(content)

                    csv_content = content.decode("utf-8-sig")  # Handle BOM
                    logger.info(f"Successfully fetched {len(csv_content)} characters")
                    return csv_content
                else:
                    logger.warning(f"HTTP {response.status} from PCC")
                    return None

        except urllib.error.HTTPError as e:
            if e.code == 429:
                logger.error("Rate limited by PCC. Increase delay between requests.")
            elif e.code == 403:
                logger.error(
                    "Access denied (403). May need to update User-Agent or check IP restrictions."
                )
            else:
                logger.error(f"HTTP Error {e.code}: {e.reason}")
            return None
        except urllib.error.URLError as e:
            logger.error(f"URL Error: {e.reason}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return None
        finally:
            # Be nice to the server
            time.sleep(self.delay)

    def parse_csv(self, csv_content: str) -> List[ProcurementRecord]:
        """
        Parse CSV content into procurement records.

        Args:
            csv_content: Raw CSV string

        Returns:
            List of ProcurementRecord objects
        """
        records = []

        try:
            lines = csv_content.strip().split("\n")
            if not lines:
                logger.warning("Empty CSV content")
                return records

            # Parse header
            reader = csv.DictReader(lines)

            for row in reader:
                try:
                    record = ProcurementRecord(
                        case_id=row.get("caseId", "").strip(),
                        case_name=row.get("caseName", "").strip(),
                        agency=row.get("agency", "").strip(),
                        publish_date=row.get("publishDate", "").strip(),
                        award_date=row.get("awardDate", "").strip() or None,
                        budget_amount=self._parse_amount(row.get("budgetAmount", "")),
                        award_amount=self._parse_amount(row.get("awardAmount", "")),
                        vendor_name=row.get("vendorName", "").strip() or None,
                        vendor_id=row.get("vendorId", "").strip() or None,
                        status=row.get("status", "unknown").strip(),
                        category=row.get("category", "unknown").strip(),
                        source_url=self.BASE_URL,
                        retrieval_date=datetime.now().isoformat(),
                        confidence="high" if row.get("vendorId") else "medium",
                        notes="",
                    )
                    records.append(record)

                except Exception as e:
                    logger.warning(f"Error parsing row: {str(e)}")
                    continue

            logger.info(f"Parsed {len(records)} records from CSV")

        except Exception as e:
            logger.error(f"Error parsing CSV: {str(e)}")

        return records

    def _parse_amount(self, amount_str: str) -> Optional[float]:
        """Parse amount string to float, handling various formats."""
        if not amount_str:
            return None

        try:
            # Remove currency symbols and commas
            cleaned = (
                amount_str.replace(",", "").replace("NT$", "").replace("$", "").strip()
            )
            return float(cleaned) if cleaned else None
        except ValueError:
            logger.warning(f"Could not parse amount: {amount_str}")
            return None

    def collect_date_range(self, date_from: str, date_to: str) -> Dict[str, Any]:
        """
        Collect procurement data for a date range.

        Args:
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)

        Returns:
            Collection results with metadata
        """
        results = {
            "date_range": {"from": date_from, "to": date_to},
            "collection_date": datetime.now().isoformat(),
            "records_collected": 0,
            "errors": [],
        }

        try:
            # Validate dates
            datetime.strptime(date_from, "%Y-%m-%d")
            datetime.strptime(date_to, "%Y-%m-%d")

            # Fetch data
            csv_content = self.fetch_csv_data(date_from, date_to)
            if not csv_content:
                results["errors"].append("Failed to fetch data from PCC")
                return results

            # Parse records
            records = self.parse_csv(csv_content)
            self.collected_records.extend(records)
            results["records_collected"] = len(records)

            logger.info(f"Collected {len(records)} procurement records")

        except ValueError as e:
            error_msg = f"Invalid date format: {str(e)}. Use YYYY-MM-DD."
            logger.error(error_msg)
            results["errors"].append(error_msg)
        except Exception as e:
            error_msg = f"Error collecting data: {str(e)}"
            logger.error(error_msg)
            results["errors"].append(error_msg)

        return results

    def filter_by_keywords(self, keywords: List[str]) -> List[ProcurementRecord]:
        """
        Filter records by keywords in case name or agency.

        Args:
            keywords: List of keywords to search for

        Returns:
            Filtered list of records
        """
        if not keywords:
            return self.collected_records

        filtered = []
        keywords_lower = [k.lower() for k in keywords]

        for record in self.collected_records:
            text = f"{record.case_name} {record.agency}".lower()
            if any(keyword in text for keyword in keywords_lower):
                filtered.append(record)

        logger.info(f"Filtered {len(filtered)} records matching keywords: {keywords}")
        return filtered

    def save_data(
        self,
        filename: Optional[str] = None,
        filtered_records: Optional[List[ProcurementRecord]] = None,
    ) -> str:
        """
        Save collected data to JSON file.

        Args:
            filename: Output filename (default: auto-generated)
            filtered_records: Optional subset to save (default: all records)

        Returns:
            Path to saved file
        """
        records = filtered_records or self.collected_records

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"procurement_{timestamp}.json"

        output_path = self.output_dir / filename

        try:
            data = {
                "metadata": {
                    "export_date": datetime.now().isoformat(),
                    "record_count": len(records),
                    "source": "Public Construction Commission (PCC)",
                    "scraper_version": "1.0.0",
                },
                "records": [record.to_dict() for record in records],
            }

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.info(f"Saved {len(records)} records to {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Error saving data: {str(e)}")
            raise


def main():
    """Main entry point with CLI argument handling."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Collect Taiwan procurement data from PCC"
    )
    parser.add_argument(
        "--from",
        "-f",
        dest="date_from",
        default="2024-01-01",
        help="Start date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--to", "-t", dest="date_to", default="2024-12-31", help="End date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--keywords",
        "-k",
        nargs="+",
        help="Keywords to filter (e.g., 法律扶助 廢死)",
        default=[],
    )
    parser.add_argument(
        "--delay",
        "-d",
        type=float,
        default=1.0,
        help="Delay between requests (seconds)",
    )
    parser.add_argument(
        "--output", "-o", default="data/raw/pcc", help="Output directory"
    )

    args = parser.parse_args()

    try:
        # Initialize scraper
        scraper = PCCScraper(output_dir=args.output, delay=args.delay)

        # Collect data
        results = scraper.collect_date_range(args.date_from, args.date_to)

        if results["records_collected"] == 0:
            logger.warning("No records collected")
            sys.exit(1)

        # Filter if keywords provided
        if args.keywords:
            filtered = scraper.filter_by_keywords(args.keywords)
            output_file = scraper.save_data(filtered_records=filtered)
            print(
                f"\nFiltered {len(filtered)} records matching keywords: {args.keywords}"
            )
        else:
            output_file = scraper.save_data()

        # Print summary
        print(f"\n{'=' * 60}")
        print("Procurement Data Collection Complete")
        print(f"{'=' * 60}")
        print(f"Date range: {args.date_from} to {args.date_to}")
        print(f"Records collected: {results['records_collected']}")
        print(f"Output file: {output_file}")

        if results["errors"]:
            print(f"\nWarnings ({len(results['errors'])}):")
            for error in results["errors"]:
                print(f"  - {error}")

        print(f"{'=' * 60}\n")

        sys.exit(0)

    except KeyboardInterrupt:
        logger.info("Collection interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
