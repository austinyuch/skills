#!/usr/bin/env python3
"""
Taiwan Civic Budget Tracker - Streamlit Web Interface
Interactive dashboard for budget and procurement data visualization.

Run with: streamlit run app.py
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

import streamlit as st
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Taiwan Civic Budget Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .highlight {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 10px;
        margin: 10px 0;
    }
</style>
""",
    unsafe_allow_html=True,
)


def load_data_files(data_dir: str = "data") -> Dict[str, Any]:
    """Load all available data files."""
    data = {
        "budget": [],
        "procurement": [],
        "entities": [],
        "relationships": [],
        "validation": [],
    }

    data_path = Path(data_dir)

    # Load budget data
    budget_files = list(data_path.glob("raw/budget/*.json"))
    for f in budget_files:
        try:
            with open(f, "r", encoding="utf-8") as file:
                content = json.load(file)
                data["budget"].extend(content.get("records", []))
        except Exception as e:
            logger.warning(f"Error loading {f}: {e}")

    # Load procurement data
    pcc_files = list(data_path.glob("raw/pcc/*.json"))
    for f in pcc_files:
        try:
            with open(f, "r", encoding="utf-8") as file:
                content = json.load(file)
                data["procurement"].extend(content.get("records", []))
        except Exception as e:
            logger.warning(f"Error loading {f}: {e}")

    # Load network data
    entity_files = list(data_path.glob("processed/*_entities.json"))
    for f in entity_files:
        try:
            with open(f, "r", encoding="utf-8") as file:
                content = json.load(file)
                data["entities"].extend(content.get("entities", []))
        except Exception as e:
            logger.warning(f"Error loading {f}: {e}")

    rel_files = list(data_path.glob("processed/*_relationships.json"))
    for f in rel_files:
        try:
            with open(f, "r", encoding="utf-8") as file:
                content = json.load(file)
                data["relationships"].extend(content.get("relationships", []))
        except Exception as e:
            logger.warning(f"Error loading {f}: {e}")

    return data


def render_sidebar():
    """Render sidebar navigation."""
    st.sidebar.markdown("## 📊 Navigation")

    page = st.sidebar.radio(
        "Select View:",
        [
            "🏠 Overview",
            "💰 Budget Analysis",
            "📋 Procurement Data",
            "🕸️ Network Visualization",
            "✅ Data Quality",
            "🔍 Search & Filter",
        ],
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📁 Data Sources")
    st.sidebar.markdown("- [Legal Aid Foundation](https://www.laf.org.tw)")
    st.sidebar.markdown("- [PCC Open Data](https://web.pcc.gov.tw)")
    st.sidebar.markdown("- [Judicial Yuan](https://www.judicial.gov.tw)")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📚 Documentation")
    st.sidebar.markdown("- [SKILL.md](../SKILL.md)")
    st.sidebar.markdown("- [Data Sources](../references/data-sources.md)")

    return page


def render_overview(data: Dict[str, Any]):
    """Render overview dashboard."""
    st.markdown(
        '<div class="main-header">Taiwan Civic Budget Tracker</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sub-header">Monitor government budget flows and procurement relationships</div>',
        unsafe_allow_html=True,
    )

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        budget_count = len(data["budget"])
        st.metric(
            "Budget Records",
            f"{budget_count:,}",
            help="Total budget data points collected",
        )

    with col2:
        proc_count = len(data["procurement"])
        st.metric(
            "Procurement Cases",
            f"{proc_count:,}",
            help="Total procurement records from PCC",
        )

    with col3:
        entity_count = len(data["entities"])
        st.metric(
            "Entities",
            f"{entity_count:,}",
            help="Agencies, vendors, and persons in network",
        )

    with col4:
        rel_count = len(data["relationships"])
        st.metric(
            "Relationships", f"{rel_count:,}", help="Connections between entities"
        )

    st.markdown("---")

    # Recent activity
    st.markdown("### 📈 Recent Activity")

    if data["procurement"]:
        df_proc = pd.DataFrame(data["procurement"])
        if "publish_date" in df_proc.columns:
            df_proc["publish_date"] = pd.to_datetime(
                df_proc["publish_date"], errors="coerce"
            )
            recent = df_proc.sort_values("publish_date", ascending=False).head(5)

            st.markdown("**Latest Procurement Cases:**")
            for _, row in recent.iterrows():
                amount = row.get("award_amount", 0) or row.get("budget_amount", 0)
                amount_str = f"NT${amount:,.0f}" if amount else "N/A"
                st.markdown(
                    f"- **{row['case_name']}** ({row['agency']}) - {amount_str}"
                )

    # Data quality summary
    st.markdown("---")
    st.markdown("### 📊 Data Quality Summary")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Budget Data**")
        if data["budget"]:
            high_conf = sum(1 for r in data["budget"] if r.get("confidence") == "high")
            total = len(data["budget"])
            confidence_rate = high_conf / total * 100

            st.progress(confidence_rate / 100)
            st.caption(f"{confidence_rate:.1f}% high confidence ({high_conf}/{total})")
        else:
            st.info("No budget data loaded")

    with col2:
        st.markdown("**Procurement Data**")
        if data["procurement"]:
            with_vendor = sum(1 for r in data["procurement"] if r.get("vendor_name"))
            total = len(data["procurement"])
            coverage = with_vendor / total * 100

            st.progress(coverage / 100)
            st.caption(f"{coverage:.1f}% with vendor info ({with_vendor}/{total})")
        else:
            st.info("No procurement data loaded")

    # About section
    st.markdown("---")
    with st.expander("ℹ️ About This Project"):
        st.markdown("""
        **Taiwan Civic Budget Tracker** tracks government budget flows and procurement 
        relationships in Taiwan, with special focus on:
        
        - **Legal Aid Foundation** budget from Judicial Yuan
        - **Public procurement** contracts from PCC
        - **Vendor concentration** analysis
        - **Anomaly detection** for irregular patterns
        
        **Data Sources:**
        - Legal Aid Foundation financial reports
        - Public Construction Commission open data
        - Ministry of Justice lawyer database
        - Judicial Yuan case records
        
        All data includes source URLs and confidence scores for transparency.
        """)


def render_budget_analysis(data: Dict[str, Any]):
    """Render budget analysis page."""
    st.markdown("### 💰 Budget Analysis")

    if not data["budget"]:
        st.warning(
            "No budget data available. Run `python scripts/collect_budget_data.py` to collect data."
        )
        return

    df = pd.DataFrame(data["budget"])

    # Filters
    st.markdown("#### 🔍 Filters")
    col1, col2 = st.columns(2)

    with col1:
        if "agency" in df.columns:
            agencies = ["All"] + sorted(df["agency"].unique().tolist())
            selected_agency = st.selectbox("Agency", agencies)
            if selected_agency != "All":
                df = df[df["agency"] == selected_agency]

    with col2:
        if "year" in df.columns:
            years = sorted(df["year"].unique().tolist(), reverse=True)
            selected_years = st.multiselect(
                "Year", years, default=years[:3] if len(years) >= 3 else years
            )
            if selected_years:
                df = df[df["year"].isin(selected_years)]

    # Summary statistics
    st.markdown("---")
    st.markdown("#### 📊 Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        total_amount = df["amount"].sum() if "amount" in df.columns else 0
        st.metric("Total Amount", f"NT${total_amount:,.0f}")

    with col2:
        record_count = len(df)
        st.metric("Records", f"{record_count:,}")

    with col3:
        if "category" in df.columns:
            categories = df["category"].nunique()
            st.metric("Categories", f"{categories}")

    # Data table
    st.markdown("---")
    st.markdown("#### 📋 Budget Records")

    display_cols = ["agency", "year", "category", "amount", "confidence", "source_url"]
    available_cols = [c for c in display_cols if c in df.columns]

    st.dataframe(df[available_cols], use_container_width=True, hide_index=True)

    # Export
    st.markdown("---")
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download as CSV",
        data=csv,
        file_name=f"budget_data_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )


def render_procurement_data(data: Dict[str, Any]):
    """Render procurement data page."""
    st.markdown("### 📋 Procurement Data")

    if not data["procurement"]:
        st.warning("No procurement data available. Run collection scripts first.")
        return

    df = pd.DataFrame(data["procurement"])

    # Filters
    st.markdown("#### 🔍 Filters")

    col1, col2, col3 = st.columns(3)

    with col1:
        if "agency" in df.columns:
            agencies = ["All"] + sorted(df["agency"].unique().tolist())
            selected_agency = st.selectbox("Agency", agencies, key="proc_agency")
            if selected_agency != "All":
                df = df[df["agency"] == selected_agency]

    with col2:
        if "status" in df.columns:
            statuses = ["All"] + sorted(df["status"].unique().tolist())
            selected_status = st.selectbox("Status", statuses, key="proc_status")
            if selected_status != "All":
                df = df[df["status"] == selected_status]

    with col3:
        if "category" in df.columns:
            categories = ["All"] + sorted(df["category"].unique().tolist())
            selected_category = st.selectbox(
                "Category", categories, key="proc_category"
            )
            if selected_category != "All":
                df = df[df["category"] == selected_category]

    # Keyword search
    search_term = st.text_input("🔎 Search by keyword (case name, vendor, etc.)")
    if search_term:
        search_cols = ["case_name", "vendor_name", "agency"]
        mask = pd.Series([False] * len(df))
        for col in search_cols:
            if col in df.columns:
                mask |= df[col].str.contains(search_term, case=False, na=False)
        df = df[mask]

    # Summary
    st.markdown("---")
    st.markdown("#### 📊 Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_budget = df["budget_amount"].sum() if "budget_amount" in df.columns else 0
        st.metric("Total Budget", f"NT${total_budget:,.0f}")

    with col2:
        total_award = df["award_amount"].sum() if "award_amount" in df.columns else 0
        st.metric("Total Awarded", f"NT${total_award:,.0f}")

    with col3:
        record_count = len(df)
        st.metric("Cases", f"{record_count:,}")

    with col4:
        if "vendor_name" in df.columns:
            vendor_count = df["vendor_name"].nunique()
            st.metric("Unique Vendors", f"{vendor_count}")

    # Data table
    st.markdown("---")
    st.markdown(f"#### 📋 Procurement Records ({len(df)} shown)")

    # Pagination
    page_size = 50
    total_pages = max(1, (len(df) + page_size - 1) // page_size)
    page_num = st.number_input("Page", min_value=1, max_value=total_pages, value=1) - 1

    start_idx = page_num * page_size
    end_idx = min(start_idx + page_size, len(df))
    page_df = df.iloc[start_idx:end_idx]

    display_cols = [
        "case_id",
        "case_name",
        "agency",
        "publish_date",
        "award_date",
        "budget_amount",
        "award_amount",
        "vendor_name",
        "status",
        "source_url",
    ]
    available_cols = [c for c in display_cols if c in page_df.columns]

    st.dataframe(page_df[available_cols], use_container_width=True, hide_index=True)

    st.caption(f"Showing records {start_idx + 1} to {end_idx} of {len(df)}")

    # Export
    st.markdown("---")
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv,
        file_name=f"procurement_data_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )


def render_network_visualization(data: Dict[str, Any]):
    """Render network visualization page."""
    st.markdown("### 🕸️ Network Visualization")

    if not data["entities"] or not data["relationships"]:
        st.warning("No network data available. Run network analysis first.")
        return

    # Network statistics
    st.markdown("#### 📊 Network Statistics")

    col1, col2, col3 = st.columns(3)

    with col1:
        entity_types = {}
        for e in data["entities"]:
            etype = e.get("type", "unknown")
            entity_types[etype] = entity_types.get(etype, 0) + 1

        st.metric("Total Entities", len(data["entities"]))
        for etype, count in sorted(entity_types.items()):
            st.caption(f"- {etype}: {count}")

    with col2:
        rel_types = {}
        for r in data["relationships"]:
            rtype = r.get("type", "unknown")
            rel_types[rtype] = rel_types.get(rtype, 0) + 1

        st.metric("Total Relationships", len(data["relationships"]))
        for rtype, count in sorted(rel_types.items()):
            st.caption(f"- {rtype}: {count}")

    with col3:
        # Top connected entities
        connection_counts = {}
        for r in data["relationships"]:
            src = r.get("source_id")
            tgt = r.get("target_id")
            connection_counts[src] = connection_counts.get(src, 0) + 1
            connection_counts[tgt] = connection_counts.get(tgt, 0) + 1

        top_connected = sorted(
            connection_counts.items(), key=lambda x: x[1], reverse=True
        )[:5]
        st.markdown("**Most Connected:**")
        for entity_id, count in top_connected:
            entity_name = next(
                (e["name"] for e in data["entities"] if e["id"] == entity_id), entity_id
            )
            st.caption(f"- {entity_name}: {count} connections")

    # D3.js visualization placeholder
    st.markdown("---")
    st.markdown("#### 🌐 Interactive Network Graph")

    st.info("""
    Interactive D3.js network visualization would be displayed here.
    
    The visualization shows:
    - **Nodes**: Agencies (blue), Vendors (green), Cases (gray)
    - **Edges**: Award relationships with thickness proportional to amount
    - **Interactivity**: Zoom, pan, click for details, filter by type
    
    Export the network data in D3 format using:
    ```bash
    python scripts/visualization.py -e entities.json -r relationships.json
    ```
    """)

    # Export D3 data
    if st.button("📥 Export D3 Network JSON"):
        d3_data = {
            "metadata": {
                "export_date": datetime.now().isoformat(),
                "nodes": len(data["entities"]),
                "links": len(data["relationships"]),
            },
            "nodes": [
                {"id": e["id"], "name": e["name"], "group": e.get("type", "unknown")}
                for e in data["entities"]
            ],
            "links": [
                {
                    "source": r["source_id"],
                    "target": r["target_id"],
                    "type": r.get("type", "unknown"),
                }
                for r in data["relationships"]
            ],
        }

        json_str = json.dumps(d3_data, ensure_ascii=False, indent=2)
        st.download_button(
            label="Download D3 JSON",
            data=json_str,
            file_name=f"network_d3_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
        )


def render_data_quality(data: Dict[str, Any]):
    """Render data quality page."""
    st.markdown("### ✅ Data Quality Report")

    # Overall quality scores
    st.markdown("#### 📊 Quality Scores")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Budget Data**")
        if data["budget"]:
            total = len(data["budget"])
            high_conf = sum(1 for r in data["budget"] if r.get("confidence") == "high")
            with_source = sum(1 for r in data["budget"] if r.get("source_url"))

            st.progress(high_conf / total)
            st.caption(
                f"High confidence: {high_conf}/{total} ({high_conf / total * 100:.1f}%)"
            )

            st.progress(with_source / total)
            st.caption(
                f"With source URL: {with_source}/{total} ({with_source / total * 100:.1f}%)"
            )
        else:
            st.info("No budget data")

    with col2:
        st.markdown("**Procurement Data**")
        if data["procurement"]:
            total = len(data["procurement"])
            with_vendor = sum(1 for r in data["procurement"] if r.get("vendor_name"))
            with_amount = sum(1 for r in data["procurement"] if r.get("award_amount"))

            st.progress(with_vendor / total)
            st.caption(
                f"With vendor: {with_vendor}/{total} ({with_vendor / total * 100:.1f}%)"
            )

            st.progress(with_amount / total)
            st.caption(
                f"With amount: {with_amount}/{total} ({with_amount / total * 100:.1f}%)"
            )
        else:
            st.info("No procurement data")

    # Run validation
    st.markdown("---")
    st.markdown("#### 🔍 Run Validation")

    if st.button("▶️ Validate All Data"):
        with st.spinner("Validating data..."):
            # Budget validation
            if data["budget"]:
                budget_errors = []
                for r in data["budget"]:
                    if not r.get("source_url"):
                        budget_errors.append(
                            f"Missing source_url: {r.get('agency', 'Unknown')}"
                        )
                    if r.get("amount", 0) < 0:
                        budget_errors.append(f"Negative amount: {r.get('amount')}")

                if budget_errors:
                    st.error(f"Found {len(budget_errors)} issues in budget data")
                    with st.expander("View budget issues"):
                        for error in budget_errors[:10]:
                            st.markdown(f"- {error}")
                        if len(budget_errors) > 10:
                            st.caption(f"... and {len(budget_errors) - 10} more")
                else:
                    st.success("✅ Budget data validation passed")

            # Procurement validation
            if data["procurement"]:
                proc_errors = []
                for r in data["procurement"]:
                    if not r.get("case_id"):
                        proc_errors.append(f"Missing case_id")
                    budget = r.get("budget_amount", 0) or 0
                    award = r.get("award_amount", 0) or 0
                    if budget > 0 and award > budget * 1.5:
                        proc_errors.append(
                            f"Award exceeds budget by >50%: {r.get('case_name', 'Unknown')}"
                        )

                if proc_errors:
                    st.error(f"Found {len(proc_errors)} issues in procurement data")
                    with st.expander("View procurement issues"):
                        for error in proc_errors[:10]:
                            st.markdown(f"- {error}")
                        if len(proc_errors) > 10:
                            st.caption(f"... and {len(proc_errors) - 10} more")
                else:
                    st.success("✅ Procurement data validation passed")


def render_search_filter(data: Dict[str, Any]):
    """Render advanced search and filter page."""
    st.markdown("### 🔍 Advanced Search")

    # Search type
    search_type = st.radio(
        "Search in:", ["Budget Data", "Procurement Data", "All Data"]
    )

    # Search query
    query = st.text_input(
        "Enter search terms:", placeholder="e.g., '法律扶助' or 'Legal Aid'"
    )

    # Filters
    st.markdown("#### 🔧 Filters")

    col1, col2 = st.columns(2)

    with col1:
        min_amount = st.number_input(
            "Minimum amount (NT$)", min_value=0, value=0, step=100000
        )

    with col2:
        confidence_filter = st.multiselect(
            "Confidence level", ["high", "medium", "low"], default=["high", "medium"]
        )

    # Execute search
    if st.button("🔍 Search"):
        results = []

        # Search budget
        if search_type in ["Budget Data", "All Data"]:
            for r in data["budget"]:
                if query.lower() in str(r).lower():
                    if r.get("confidence") in confidence_filter:
                        if r.get("amount", 0) >= min_amount:
                            results.append({**r, "_type": "budget"})

        # Search procurement
        if search_type in ["Procurement Data", "All Data"]:
            for r in data["procurement"]:
                if query.lower() in str(r).lower():
                    if r.get("confidence") in confidence_filter:
                        amount = r.get("award_amount", 0) or r.get("budget_amount", 0)
                        if amount >= min_amount:
                            results.append({**r, "_type": "procurement"})

        # Display results
        st.markdown(f"#### 📋 Results ({len(results)} found)")

        if results:
            df_results = pd.DataFrame(results)
            st.dataframe(df_results, use_container_width=True, hide_index=True)

            # Export
            csv = df_results.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Results",
                data=csv,
                file_name=f"search_results_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )
        else:
            st.info("No results found matching your criteria")


def main():
    """Main application entry point."""
    try:
        # Load data
        with st.spinner("Loading data..."):
            data = load_data_files()

        # Render sidebar and get selected page
        page = render_sidebar()

        # Render selected page
        if page == "🏠 Overview":
            render_overview(data)
        elif page == "💰 Budget Analysis":
            render_budget_analysis(data)
        elif page == "📋 Procurement Data":
            render_procurement_data(data)
        elif page == "🕸️ Network Visualization":
            render_network_visualization(data)
        elif page == "✅ Data Quality":
            render_data_quality(data)
        elif page == "🔍 Search & Filter":
            render_search_filter(data)

    except Exception as e:
        st.error(f"Error loading application: {str(e)}")
        logger.error(f"Application error: {e}", exc_info=True)

        st.markdown("### 🐛 Troubleshooting")
        st.markdown("""
        If you're seeing this error:
        1. Check that data files exist in `data/` directory
        2. Run collection scripts: `python scripts/collect_budget_data.py`
        3. Check logs in `logs/` directory
        4. Ensure all dependencies are installed: `pip install -r scripts/requirements.txt`
        """)


if __name__ == "__main__":
    main()
