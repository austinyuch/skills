#!/usr/bin/env python3
"""
Data Validation Script
Validates collected data for completeness, accuracy, and confidence scoring.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/data_validation.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of data validation check."""

    field: str
    status: str  # pass, warning, error
    message: str
    confidence: str  # high, medium, low


class DataValidator:
    """Validates budget and procurement data quality."""

    def __init__(self):
        """Initialize validator."""
        self.validation_errors: List[ValidationResult] = []
        self.validation_warnings: List[ValidationResult] = []
        self.validation_passed: List[ValidationResult] = []

    def validate_budget_record(self, record: Dict) -> List[ValidationResult]:
        """
        Validate a single budget record.

        Args:
            record: Budget record dictionary

        Returns:
            List of validation results
        """
        results = []

        # Required fields
        required_fields = ["agency", "year", "category", "amount", "source_url"]
        for field in required_fields:
            if field not in record or record[field] is None:
                results.append(
                    ValidationResult(
                        field=field,
                        status="error",
                        message=f"Missing required field: {field}",
                        confidence="low",
                    )
                )
            else:
                results.append(
                    ValidationResult(
                        field=field,
                        status="pass",
                        message=f"Field {field} present",
                        confidence="high",
                    )
                )

        # Validate amount
        if "amount" in record and record["amount"] is not None:
            amount = record["amount"]
            if amount < 0:
                results.append(
                    ValidationResult(
                        field="amount",
                        status="error",
                        message=f"Negative amount: {amount}",
                        confidence="low",
                    )
                )
            elif amount == 0:
                results.append(
                    ValidationResult(
                        field="amount",
                        status="warning",
                        message="Zero amount",
                        confidence="medium",
                    )
                )
            elif amount > 10_000_000_000:  # > 10 billion
                results.append(
                    ValidationResult(
                        field="amount",
                        status="warning",
                        message=f"Unusually large amount: {amount}",
                        confidence="medium",
                    )
                )

        # Validate source URL
        if "source_url" in record and record["source_url"]:
            url = record["source_url"]
            if not url.startswith(("http://", "https://")):
                results.append(
                    ValidationResult(
                        field="source_url",
                        status="error",
                        message=f"Invalid URL format: {url}",
                        confidence="low",
                    )
                )

        # Validate retrieval date
        if "retrieval_date" in record and record["retrieval_date"]:
            try:
                datetime.fromisoformat(record["retrieval_date"])
                results.append(
                    ValidationResult(
                        field="retrieval_date",
                        status="pass",
                        message="Valid ISO format date",
                        confidence="high",
                    )
                )
            except ValueError:
                results.append(
                    ValidationResult(
                        field="retrieval_date",
                        status="warning",
                        message="Invalid date format",
                        confidence="medium",
                    )
                )

        # Validate confidence
        if "confidence" in record:
            valid_confidence = ["high", "medium", "low"]
            if record["confidence"] not in valid_confidence:
                results.append(
                    ValidationResult(
                        field="confidence",
                        status="warning",
                        message=f"Invalid confidence value: {record['confidence']}",
                        confidence="medium",
                    )
                )

        return results

    def validate_procurement_record(self, record: Dict) -> List[ValidationResult]:
        """
        Validate a single procurement record.

        Args:
            record: Procurement record dictionary

        Returns:
            List of validation results
        """
        results = []

        # Required fields
        required_fields = [
            "case_id",
            "case_name",
            "agency",
            "publish_date",
            "source_url",
        ]
        for field in required_fields:
            if field not in record or not record[field]:
                results.append(
                    ValidationResult(
                        field=field,
                        status="error",
                        message=f"Missing required field: {field}",
                        confidence="low",
                    )
                )

        # Validate award amount vs budget
        budget = record.get("budget_amount")
        award = record.get("award_amount")

        if budget and award:
            if award > budget * 1.5:  # Award 50% over budget
                results.append(
                    ValidationResult(
                        field="award_amount",
                        status="warning",
                        message=f"Award amount ({award}) significantly exceeds budget ({budget})",
                        confidence="medium",
                    )
                )
            elif award < budget * 0.1:  # Award 90% under budget
                results.append(
                    ValidationResult(
                        field="award_amount",
                        status="warning",
                        message=f"Award amount ({award}) much lower than budget ({budget})",
                        confidence="medium",
                    )
                )

        # Validate vendor ID format (Taiwan UBNo is 8 digits)
        vendor_id = record.get("vendor_id")
        if vendor_id:
            if not str(vendor_id).isdigit() or len(str(vendor_id)) != 8:
                results.append(
                    ValidationResult(
                        field="vendor_id",
                        status="warning",
                        message=f"Vendor ID may be invalid: {vendor_id} (expected 8 digits)",
                        confidence="medium",
                    )
                )

        # Validate dates
        publish_date = record.get("publish_date")
        award_date = record.get("award_date")

        if publish_date and award_date:
            try:
                pub_dt = datetime.strptime(publish_date, "%Y-%m-%d")
                award_dt = datetime.strptime(award_date, "%Y-%m-%d")

                if award_dt < pub_dt:
                    results.append(
                        ValidationResult(
                            field="award_date",
                            status="error",
                            message=f"Award date ({award_date}) before publish date ({publish_date})",
                            confidence="low",
                        )
                    )
            except ValueError:
                pass  # Date parsing error handled elsewhere

        return results

    def validate_dataset(self, data: Dict[str, Any], data_type: str) -> Dict[str, Any]:
        """
        Validate entire dataset.

        Args:
            data: Dataset dictionary
            data_type: 'budget' or 'procurement'

        Returns:
            Validation summary
        """
        records = data.get("records", [])
        total_records = len(records)

        all_results = []
        errors = 0
        warnings = 0
        passed = 0

        logger.info(f"Validating {total_records} {data_type} records")

        for i, record in enumerate(records):
            if data_type == "budget":
                results = self.validate_budget_record(record)
            else:
                results = self.validate_procurement_record(record)

            all_results.extend(results)

            for result in results:
                if result.status == "error":
                    errors += 1
                elif result.status == "warning":
                    warnings += 1
                else:
                    passed += 1

            # Progress logging
            if (i + 1) % 100 == 0:
                logger.info(f"Validated {i + 1}/{total_records} records")

        # Calculate overall confidence score
        total_checks = errors + warnings + passed
        if total_checks > 0:
            confidence_score = (passed + warnings * 0.5) / total_checks
        else:
            confidence_score = 0.0

        summary = {
            "validation_date": datetime.now().isoformat(),
            "data_type": data_type,
            "total_records": total_records,
            "total_checks": total_checks,
            "errors": errors,
            "warnings": warnings,
            "passed": passed,
            "confidence_score": round(confidence_score, 3),
            "overall_quality": self._quality_rating(confidence_score),
        }

        logger.info(f"Validation complete: {summary}")
        return summary

    def _quality_rating(self, score: float) -> str:
        """Convert score to quality rating."""
        if score >= 0.95:
            return "excellent"
        elif score >= 0.85:
            return "good"
        elif score >= 0.70:
            return "acceptable"
        elif score >= 0.50:
            return "poor"
        else:
            return "critical"

    def validate_file(
        self, filepath: str, data_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate data from a file.

        Args:
            filepath: Path to JSON data file
            data_type: 'budget' or 'procurement' (auto-detected if None)

        Returns:
            Validation summary
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Auto-detect data type if not specified
            if data_type is None:
                sample = data.get("records", [{}])[0]
                if "agency" in sample and "case_id" not in sample:
                    data_type = "budget"
                elif "case_id" in sample:
                    data_type = "procurement"
                else:
                    data_type = "unknown"

            return self.validate_dataset(data, data_type)

        except FileNotFoundError:
            logger.error(f"File not found: {filepath}")
            return {"error": f"File not found: {filepath}"}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {filepath}: {e}")
            return {"error": f"Invalid JSON: {e}"}
        except Exception as e:
            logger.error(f"Error validating {filepath}: {e}")
            return {"error": str(e)}


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate budget/procurement data")
    parser.add_argument("files", nargs="+", help="JSON files to validate")
    parser.add_argument(
        "--type", "-t", choices=["budget", "procurement"], help="Data type"
    )
    parser.add_argument("--output", "-o", help="Output file for validation report")

    args = parser.parse_args()

    try:
        validator = DataValidator()
        all_summaries = []

        print(f"\n{'=' * 70}")
        print("DATA VALIDATION REPORT")
        print(f"{'=' * 70}\n")

        for filepath in args.files:
            print(f"\nValidating: {filepath}")
            print("-" * 70)

            summary = validator.validate_file(filepath, args.type)
            all_summaries.append({"file": filepath, "summary": summary})

            if "error" in summary:
                print(f"ERROR: {summary['error']}")
                continue

            print(f"Records: {summary['total_records']}")
            print(f"Checks:  {summary['total_checks']}")
            print(f"Passed:  {summary['passed']}")
            print(f"Warnings: {summary['warnings']}")
            print(f"Errors:  {summary['errors']}")
            print(f"Score:   {summary['confidence_score']:.1%}")
            print(f"Quality: {summary['overall_quality'].upper()}")

        print(f"\n{'=' * 70}")
        print("VALIDATION COMPLETE")
        print(f"{'=' * 70}\n")

        # Save report if requested
        if args.output:
            report = {
                "validation_date": datetime.now().isoformat(),
                "files_validated": len(args.files),
                "results": all_summaries,
            }

            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)

            print(f"Report saved to: {args.output}")

        # Exit with error code if any critical issues
        critical_count = sum(
            1
            for s in all_summaries
            if s["summary"].get("overall_quality") == "critical"
        )

        sys.exit(1 if critical_count > 0 else 0)

    except KeyboardInterrupt:
        logger.info("Validation interrupted")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
