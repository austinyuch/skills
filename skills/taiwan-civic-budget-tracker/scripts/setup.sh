#!/bin/bash
# Setup script for Taiwan Civic Budget Tracker
# Usage: ./setup.sh

set -e  # Exit on error

echo "=========================================="
echo "Taiwan Civic Budget Tracker Setup"
echo "=========================================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

required_version="3.9"
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"; then
    echo "ERROR: Python 3.9+ required. Current: $python_version"
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "ERROR: pip3 not found. Please install pip."
    exit 1
fi

echo ""
echo "Step 1: Creating directory structure..."
mkdir -p {logs,data/{raw/{budget,pcc,moea,judicial,moj},processed/{entities,relationships},reports/{charts,analysis}},config,references}

echo ""
echo "Step 2: Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi

echo ""
echo "Step 3: Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Step 4: Installing dependencies..."
pip install --upgrade pip
pip install -r scripts/requirements.txt

echo ""
echo "Step 5: Installing Playwright browsers..."
playwright install chromium

echo ""
echo "Step 6: Setting up pre-commit hooks (optional)..."
if command -v pre-commit &> /dev/null; then
    pre-commit install
    echo "Pre-commit hooks installed."
else
    echo "Skipping pre-commit setup (not installed)."
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To get started:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Collect budget data: python scripts/collect_budget_data.py"
echo "  3. Collect procurement: python scripts/collect_procurement.py -f 2024-01-01 -t 2024-12-31"
echo "  4. Analyze network: python scripts/network_analysis.py data/raw/pcc/procurement_*.json"
echo ""
echo "For more information, see:"
echo "  - SKILL.md - Complete usage guide"
echo "  - README.md - Quick start guide"
echo "  - references/data-sources.md - Data source documentation"
echo ""
