# Taiwan Civic Budget Tracker

Track government budget flows and procurement relationships in Taiwan.

## Quick Start

```bash
# Clone and setup
git clone <repository>
cd taiwan-civic-budget-tracker
./scripts/setup.sh

# Activate environment
source venv/bin/activate

# Collect budget data
python scripts/collect_budget_data.py

# Collect procurement data (2024)
python scripts/collect_procurement.py -f 2024-01-01 -t 2024-12-31 -k 法律扶助

# Analyze network
python scripts/network_analysis.py data/raw/pcc/procurement_*.json

# Generate visualizations
python scripts/visualization.py -p data/raw/pcc/procurement_*.json
```

## Features

- **Budget Tracking**: Monitor Legal Aid Foundation budget from Judicial Yuan
- **Procurement Monitoring**: Track public contracts from PCC (Public Construction Commission)
- **Network Analysis**: Identify vendor concentration and anomalies
- **Data Provenance**: Every record has source URL and confidence score
- **Entity Disambiguation**: Handle name collisions with birth year tracking

## Data Sources

| Source | URL | Status |
|--------|-----|--------|
| PCC Procurement | https://web.pcc.gov.tw/pis/openData/awardCSV | ✅ CSV API |
| Legal Aid Foundation | https://www.laf.org.tw/financialReport/1 | ✅ Public reports |
| MOJ Lawyer Query | https://lawyerbc.moj.gov.tw/ | ✅ Web interface |
| Judicial Yuan Search | https://lawsearch.judicial.gov.tw/ | ✅ Web search |

## Documentation

- `SKILL.md` - Complete usage guide
- `references/data-sources.md` - Data source details
- `references/data-model.md` - Entity relationship diagram
- `references/scraping-guide.md` - Anti-detection techniques

## Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=scripts --cov-report=html
```

## Project Structure

```
taiwan-civic-budget-tracker/
├── scripts/           # Collection and analysis scripts
├── data/             # Raw and processed data
│   ├── raw/         # Original scraped data
│   └── processed/   # Cleaned and analyzed data
├── tests/           # Unit tests
├── references/      # Documentation
└── logs/           # Execution logs
```

## License

MIT License - See LICENSE file

## Contributing

See `references/lesson-learned.md` for improvement roadmap.
