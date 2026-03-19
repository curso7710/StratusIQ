"""Findings table component"""
import streamlit as st
import pandas as pd
from typing import List, Dict
from utils.helpers import format_currency


def render_findings_table(findings: List[Dict], dependency_graph=None):
    """Render findings table with filters"""
    if not findings:
        st.info("No findings to display")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        category_filter = st.multiselect(
            "Category",
            options=["cost", "security"],
            default=["cost", "security"]
        )
    
    with col2:
        severity_filter = st.multiselect(
            "Severity",
            options=["critical", "high", "medium", "low"],
            default=["critical", "high", "medium", "low"]
        )
    
    with col3:
        min_savings = st.number_input(
            "Min Monthly Savings ($)",
            min_value=0.0,
            value=0.0,
            step=10.0
        )
    
    # Filter findings
    filtered_findings = [
        f for f in findings
        if f['category'] in category_filter
        and f['severity'] in severity_filter
        and f.get('estimated_monthly_savings', 0) >= min_savings
    ]
    
    st.write(f"Showing {len(filtered_findings)} of {len(findings)} findings")
    
    # Convert to DataFrame
    df_data = []
    for finding in filtered_findings:
        df_data.append({
            "Priority": finding.get('priority_score', 0),
            "Title": finding.get('title', ''),
            "Category": finding.get('category', ''),
            "Severity": finding.get('severity', ''),
            "Monthly Savings": format_currency(finding.get('estimated_monthly_savings', 0)),
            "Risk": finding.get('change_risk', ''),
            "Confidence": finding.get('confidence', ''),
            "ID": finding.get('id', '')
        })
    
    if df_data:
        df = pd.DataFrame(df_data)
        
        # Style the dataframe
        def highlight_severity(row):
            severity = row['Severity']
            if severity == 'critical':
                return ['background-color: #ff4444'] * len(row)
            elif severity == 'high':
                return ['background-color: #ff8844'] * len(row)
            elif severity == 'medium':
                return ['background-color: #ffbb44'] * len(row)
            else:
                return [''] * len(row)
        
        # Display table
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Priority": st.column_config.NumberColumn(
                    "Priority Score",
                    format="%.2f"
                ),
                "Monthly Savings": st.column_config.TextColumn(
                    "Monthly Savings"
                )
            }
        )
        
        # Finding selection
        st.subheader("View Finding Details")
        selected_id = st.selectbox(
            "Select a finding to view details",
            options=[f['ID'] for f in df_data],
            format_func=lambda x: next(f['Title'] for f in df_data if f['ID'] == x)
        )
        
        if selected_id:
            selected_finding = next(f for f in filtered_findings if f['id'] == selected_id)
            return selected_finding, dependency_graph
    
    return None, None
