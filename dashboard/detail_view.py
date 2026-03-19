"""Finding detail view component"""
import streamlit as st
from typing import Dict
import json
from utils.helpers import format_currency
from fixes.terraform_patch_generator import TerraformPatchGenerator
from fixes.cli_fix_generator import CLIFixGenerator
from llm.explanation_engine import ExplanationEngine
from impact.impact_simulator import ImpactSimulator


def render_finding_detail(finding: Dict, dependency_graph=None):
    """Render detailed view of a finding"""
    if not finding:
        return
    
    st.header(finding.get('title', 'Finding Details'))
    
    # Overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        severity = finding.get('severity', 'unknown')
        severity_color = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢'
        }.get(severity, '⚪')
        st.metric("Severity", f"{severity_color} {severity.upper()}")
    
    with col2:
        st.metric("Category", finding.get('category', 'unknown').upper())
    
    with col3:
        savings = finding.get('estimated_monthly_savings', 0)
        st.metric("Monthly Savings", format_currency(savings))
    
    with col4:
        annual_savings = savings * 12
        st.metric("Annual Savings", format_currency(annual_savings))
    
    # Tabs for different sections
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Evidence", 
        "🔧 Terraform Patch", 
        "💻 CLI Commands", 
        "📖 Explanation",
        "🔗 Impact",
        "⚡ Change Impact Simulation"
    ])
    
    with tab1:
        st.subheader("Evidence")
        evidence = finding.get('evidence', {})
        st.json(evidence)
        
        st.subheader("Metadata")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Confidence:** {finding.get('confidence', 'unknown')}")
            st.write(f"**Change Risk:** {finding.get('change_risk', 'unknown')}")
        with col2:
            st.write(f"**Priority Score:** {finding.get('priority_score', 0):.2f}")
            st.write(f"**Finding ID:** `{finding.get('id', 'unknown')}`")
    
    with tab2:
        st.subheader("Terraform Patch")
        st.write("Apply this patch to your Terraform configuration:")
        
        patch_gen = TerraformPatchGenerator()
        patch = patch_gen.generate_patch(finding)
        
        st.code(patch, language="hcl")
        
        st.warning("⚠️ Review the patch carefully before applying. Test in non-production first.")
    
    with tab3:
        st.subheader("AWS CLI Commands")
        st.write("Execute these commands to remediate the issue:")
        
        cli_gen = CLIFixGenerator()
        cli_commands = cli_gen.generate_cli_command(finding)
        
        st.code(cli_commands, language="bash")
        
        st.warning("⚠️ These commands will modify your AWS infrastructure. Review carefully before execution.")
        st.info("💡 Tip: Test commands with --dry-run flag when available")
    
    with tab4:
        st.subheader("Detailed Explanation")
        
        explainer = ExplanationEngine()
        explanation = explainer.explain_finding(finding)
        
        st.markdown(explanation)
    
    with tab5:
        st.subheader("Impact Analysis")
        
        affected = finding.get('affected_resources', [])
        blast_radius = finding.get('blast_radius', [])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Affected Resources:**")
            if affected:
                for resource in affected:
                    st.write(f"- `{resource}`")
            else:
                st.write("None")
        
        with col2:
            st.write("**Blast Radius:**")
            if blast_radius:
                st.write(f"{len(blast_radius)} connected resources")
                with st.expander("View connected resources"):
                    for resource in blast_radius:
                        st.write(f"- `{resource}`")
            else:
                st.write("No connected resources")
    
    with tab6:
        st.subheader("⚡ Change Impact Simulation")
        st.write("Predict the operational impact of applying this fix")
        
        # Run impact simulation
        simulator = ImpactSimulator()
        impact = simulator.simulate_change(finding, dependency_graph)
        
        # Risk level with color coding
        risk_level = impact.get('risk_level', 'Unknown')
        risk_colors = {
            'Low': '🟢',
            'Medium': '🟡',
            'High': '🔴'
        }
        risk_color = risk_colors.get(risk_level, '⚪')
        
        # Display key metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Risk Level", f"{risk_color} {risk_level}")
        
        with col2:
            downtime_prob = impact.get('downtime_probability', 'Unknown')
            st.metric("Downtime Probability", downtime_prob)
        
        with col3:
            estimated_downtime = impact.get('estimated_downtime', 'Unknown')
            st.metric("Estimated Downtime", estimated_downtime)
        
        # Change type
        st.markdown("---")
        st.markdown(f"**Change Type:** `{impact.get('change_type', 'Unknown')}`")
        st.caption(impact.get('downtime_details', ''))
        
        # Affected services
        st.markdown("---")
        st.subheader("🎯 Affected Services")
        affected_services = impact.get('affected_services', [])
        if affected_services:
            for service in affected_services:
                st.write(f"• {service}")
        else:
            st.info("No directly affected services identified")
        
        # Blast radius
        blast_radius_count = impact.get('blast_radius_count', 0)
        if blast_radius_count > 0:
            st.warning(f"⚠️ This change may affect {blast_radius_count} connected resources")
        
        # Recommendations
        st.markdown("---")
        st.subheader("💡 Recommendations")
        recommendations = impact.get('recommendations', [])
        for rec in recommendations:
            st.write(rec)
        
        # Safety checks
        st.markdown("---")
        st.subheader("✅ Safety Checklist")
        st.write("Complete these checks before applying the fix:")
        
        safety_checks = impact.get('safety_checks', [])
        for check in safety_checks:
            st.write(check)
        
        # Rollback plan
        st.markdown("---")
        st.subheader("🔄 Rollback Plan")
        st.write("If something goes wrong, follow these steps:")
        
        rollback_steps = impact.get('rollback_steps', [])
        rollback_text = '\n'.join(rollback_steps)
        st.code(rollback_text, language='bash')
        
        # Complexity score
        complexity = simulator.get_change_complexity_score(impact)
        st.markdown("---")
        st.subheader("📊 Change Complexity Score")
        
        # Progress bar for complexity
        if complexity < 30:
            complexity_label = "Simple"
            bar_color = "green"
        elif complexity < 60:
            complexity_label = "Moderate"
            bar_color = "orange"
        else:
            complexity_label = "Complex"
            bar_color = "red"
        
        st.progress(complexity / 100)
        st.write(f"**{complexity}/100** - {complexity_label} change")
        st.caption("Complexity is based on risk level, downtime probability, and blast radius")
        
        # Final warning for high-risk changes
        if risk_level == "High":
            st.error("⚠️ HIGH RISK CHANGE: This operation requires careful planning and should be tested in non-production first.")
        elif risk_level == "Medium":
            st.warning("⚡ MEDIUM RISK CHANGE: Schedule during maintenance window and monitor closely.")
        else:
            st.success("✅ LOW RISK CHANGE: This change is relatively safe but still requires review.")
