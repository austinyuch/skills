#!/usr/bin/env python3
"""
Unit Tests for Taiwan Budget Tracker

Run with: pytest tests/ -v
Or: python -m pytest tests/ --cov=scripts --cov-report=html
"""

import json
import sys
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from collect_budget_data import BudgetCollector, BudgetRecord
from collect_procurement import PCCScraper, ProcurementRecord
from network_analysis import NetworkAnalyzer, Entity, Relationship


class TestBudgetRecord(unittest.TestCase):
    """Test BudgetRecord dataclass."""

    def test_create_record(self):
        """Test creating a budget record."""
        record = BudgetRecord(
            agency="Legal Aid Foundation",
            year=2025,
            category="Income",
            amount=1520000000,
            source_url="https://www.laf.org.tw/financialReport/1",
            retrieval_date="2024-03-15T10:00:00",
            confidence="high",
            notes="Test record",
        )

        self.assertEqual(record.agency, "Legal Aid Foundation")
        self.assertEqual(record.year, 2025)
        self.assertEqual(record.amount, 1520000000)
        self.assertEqual(record.confidence, "high")

    def test_to_dict(self):
        """Test conversion to dictionary."""
        record = BudgetRecord(
            agency="Test Agency",
            year=2024,
            category="Test",
            amount=1000000,
            source_url="http://test.com",
            retrieval_date="2024-01-01T00:00:00",
        )

        d = record.to_dict()
        self.assertIsInstance(d, dict)
        self.assertEqual(d["agency"], "Test Agency")
        self.assertEqual(d["amount"], 1000000)


class TestBudgetCollector(unittest.TestCase):
    """Test BudgetCollector class."""

    def setUp(self):
        """Set up test fixtures."""
        self.collector = BudgetCollector(output_dir="/tmp/test_budget")

    def test_initialization(self):
        """Test collector initialization."""
        self.assertEqual(self.collector.output_dir, Path("/tmp/test_budget"))
        self.assertEqual(self.collector.collected_data, [])

    @patch("urllib.request.urlopen")
    def test_fetch_url_success(self, mock_urlopen):
        """Test successful URL fetch."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b"Test content"
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response

        result = self.collector.fetch_url("http://test.com")
        self.assertEqual(result, "Test content")

    @patch("urllib.request.urlopen")
    def test_fetch_url_http_error(self, mock_urlopen):
        """Test HTTP error handling."""
        from urllib.error import HTTPError

        mock_urlopen.side_effect = HTTPError(
            url="http://test.com", code=404, msg="Not Found", hdrs={}, fp=None
        )

        result = self.collector.fetch_url("http://test.com")
        self.assertIsNone(result)

    @patch("urllib.request.urlopen")
    def test_fetch_url_url_error(self, mock_urlopen):
        """Test URL error handling."""
        from urllib.error import URLError

        mock_urlopen.side_effect = URLError("Connection refused")

        result = self.collector.fetch_url("http://test.com")
        self.assertIsNone(result)


class TestProcurementRecord(unittest.TestCase):
    """Test ProcurementRecord dataclass."""

    def test_create_record(self):
        """Test creating a procurement record."""
        record = ProcurementRecord(
            case_id="TEST-001",
            case_name="Test Procurement",
            agency="Test Agency",
            publish_date="2024-01-01",
            award_date="2024-02-01",
            budget_amount=1000000,
            award_amount=950000,
            vendor_name="Test Vendor",
            vendor_id="12345678",
            status="awarded",
            category="construction",
            source_url="http://test.com",
            retrieval_date="2024-03-15T10:00:00",
        )

        self.assertEqual(record.case_id, "TEST-001")
        self.assertEqual(record.award_amount, 950000)
        self.assertEqual(record.vendor_id, "12345678")

    def test_to_dict(self):
        """Test conversion to dictionary."""
        record = ProcurementRecord(
            case_id="TEST-002",
            case_name="Test",
            agency="Agency",
            publish_date="2024-01-01",
            source_url="http://test.com",
            retrieval_date="2024-01-01T00:00:00",
        )

        d = record.to_dict()
        self.assertIsInstance(d, dict)
        self.assertEqual(d["case_id"], "TEST-002")


class TestPCCScraper(unittest.TestCase):
    """Test PCCScraper class."""

    def setUp(self):
        """Set up test fixtures."""
        self.scraper = PCCScraper(output_dir="/tmp/test_pcc", delay=0.1)

    def test_initialization(self):
        """Test scraper initialization."""
        self.assertEqual(self.scraper.output_dir, Path("/tmp/test_pcc"))
        self.assertEqual(self.scraper.delay, 0.1)

    def test_parse_amount_valid(self):
        """Test amount parsing with valid inputs."""
        self.assertEqual(self.scraper._parse_amount("1,000,000"), 1000000.0)
        self.assertEqual(self.scraper._parse_amount("NT$500,000"), 500000.0)
        self.assertEqual(self.scraper._parse_amount("1000"), 1000.0)

    def test_parse_amount_invalid(self):
        """Test amount parsing with invalid inputs."""
        self.assertIsNone(self.scraper._parse_amount(""))
        self.assertIsNone(self.scraper._parse_amount("invalid"))
        self.assertIsNone(self.scraper._parse_amount(None))

    def test_parse_csv_valid(self):
        """Test CSV parsing with valid data."""
        csv_content = """caseId,caseName,agency,publishDate,awardDate,budgetAmount,awardAmount,vendorName,vendorId,status,category
TEST-001,Test Case,Test Agency,2024-01-01,2024-02-01,"1,000,000","950,000",Test Vendor,12345678,awarded,construction
TEST-002,Another Case,Another Agency,2024-01-02,,,"500,000",,,pending,service"""

        records = self.scraper.parse_csv(csv_content)
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0].case_id, "TEST-001")
        self.assertEqual(records[0].award_amount, 950000.0)
        self.assertIsNone(records[1].award_date)

    def test_parse_csv_empty(self):
        """Test CSV parsing with empty content."""
        records = self.scraper.parse_csv("")
        self.assertEqual(len(records), 0)

    def test_filter_by_keywords(self):
        """Test keyword filtering."""
        # Create mock records
        records = [
            ProcurementRecord(
                case_id="TEST-001",
                case_name="Legal Aid Project",
                agency="Judicial Yuan",
                publish_date="2024-01-01",
                source_url="http://test.com",
                retrieval_date="2024-01-01T00:00:00",
            ),
            ProcurementRecord(
                case_id="TEST-002",
                case_name="Road Construction",
                agency="Transport Bureau",
                publish_date="2024-01-02",
                source_url="http://test.com",
                retrieval_date="2024-01-01T00:00:00",
            ),
        ]

        self.scraper.collected_records = records
        filtered = self.scraper.filter_by_keywords(["legal", "aid"])

        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].case_id, "TEST-001")


class TestNetworkAnalyzer(unittest.TestCase):
    """Test NetworkAnalyzer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = NetworkAnalyzer(data_dir="/tmp/test_data")

    def test_initialization(self):
        """Test analyzer initialization."""
        self.assertEqual(self.analyzer.data_dir, Path("/tmp/test_data"))
        self.assertEqual(self.analyzer.entities, {})
        self.assertEqual(self.analyzer.relationships, [])

    def test_load_procurement_data_file_not_found(self):
        """Test handling of missing file."""
        records = self.analyzer.load_procurement_data("/nonexistent/file.json")
        self.assertEqual(records, [])

    def test_build_network(self):
        """Test network building from records."""
        records = [
            {
                "agency": "Test Agency",
                "case_id": "TEST-001",
                "case_name": "Test Case",
                "vendor_name": "Test Vendor",
                "vendor_id": "12345678",
                "award_amount": 1000000,
                "award_date": "2024-02-01",
                "source_url": "http://test.com",
                "confidence": "high",
            },
            {
                "agency": "Test Agency",
                "case_id": "TEST-002",
                "case_name": "Another Case",
                "vendor_name": "Test Vendor",
                "vendor_id": "12345678",
                "award_amount": 500000,
                "award_date": "2024-03-01",
                "source_url": "http://test.com",
                "confidence": "high",
            },
        ]

        stats = self.analyzer.build_network(records)

        self.assertEqual(stats["entities"], 2)  # 1 agency + 1 vendor
        self.assertEqual(stats["relationships"], 2)  # 2 awards
        self.assertEqual(stats["agencies"], 1)
        self.assertEqual(stats["vendors"], 1)

    def test_analyze_vendor_concentration(self):
        """Test vendor concentration analysis."""
        # Build network first
        records = [
            {
                "agency": "Agency A",
                "case_id": "001",
                "case_name": "Case 1",
                "vendor_name": "Vendor X",
                "vendor_id": "111",
                "award_amount": 1000000,
                "award_date": "2024-01-01",
                "source_url": "http://test.com",
                "confidence": "high",
            },
            {
                "agency": "Agency B",
                "case_id": "002",
                "case_name": "Case 2",
                "vendor_name": "Vendor X",
                "vendor_id": "111",
                "award_amount": 2000000,
                "award_date": "2024-02-01",
                "source_url": "http://test.com",
                "confidence": "high",
            },
            {
                "agency": "Agency C",
                "case_id": "003",
                "case_name": "Case 3",
                "vendor_name": "Vendor Y",
                "vendor_id": "222",
                "award_amount": 500000,
                "award_date": "2024-03-01",
                "source_url": "http://test.com",
                "confidence": "high",
            },
        ]

        self.analyzer.build_network(records)
        vendors = self.analyzer.analyze_vendor_concentration()

        self.assertEqual(len(vendors), 2)
        self.assertEqual(vendors[0]["vendor_name"], "Vendor X")  # Most cases
        self.assertEqual(vendors[0]["case_count"], 2)
        self.assertEqual(vendors[0]["total_amount"], 3000000)


class TestIntegration(unittest.TestCase):
    """Integration tests for the full workflow."""

    def test_full_workflow(self):
        """Test complete workflow from procurement to network analysis."""
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            # Step 1: Create procurement data
            scraper = PCCScraper(output_dir=f"{tmpdir}/pcc", delay=0)

            records = [
                ProcurementRecord(
                    case_id="INT-001",
                    case_name="Integration Test",
                    agency="Test Agency",
                    publish_date="2024-01-01",
                    award_date="2024-02-01",
                    budget_amount=1000000,
                    award_amount=950000,
                    vendor_name="Integration Vendor",
                    vendor_id="99999999",
                    status="awarded",
                    category="test",
                    source_url="http://test.com",
                    retrieval_date="2024-01-01T00:00:00",
                )
            ]

            scraper.collected_records = records
            proc_file = scraper.save_data(filename="test_procurement.json")

            # Step 2: Analyze network
            analyzer = NetworkAnalyzer(data_dir=tmpdir)
            proc_records = analyzer.load_procurement_data(proc_file)
            self.assertEqual(len(proc_records), 1)

            stats = analyzer.build_network(proc_records)
            self.assertEqual(stats["records_processed"], 1)

            # Verify file was created
            self.assertTrue(os.path.exists(proc_file))


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestBudgetRecord))
    suite.addTests(loader.loadTestsFromTestCase(TestBudgetCollector))
    suite.addTests(loader.loadTestsFromTestCase(TestProcurementRecord))
    suite.addTests(loader.loadTestsFromTestCase(TestPCCScraper))
    suite.addTests(loader.loadTestsFromTestCase(TestNetworkAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
