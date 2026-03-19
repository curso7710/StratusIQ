"""StratusIQ - Cloud Cost & Security Intelligence Platform"""
import streamlit as st
import json
from scanner.terraform_parser import TerraformParser
from scanner.aws_scanner import AWSScanner
from graph.dependency_graph import DependencyGraph
from engine.rule_engine import RuleEngine
from scoring.priority_scoring import PriorityScorer
from dashboard.findings_table import render_findings_table
from dashboard.detail_view import render_finding_detail
from dashboard.graph_view import render_graph_view
from report.report_generator import ReportGenerator
from utils.logging_utils import setup_logger, log_scan_event
import plotly.express as px
import plotly.graph_objects as go

logger = setup_logger(__name__)

# Page config
st.set_page_config(
    page_title="StratusIQ",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'resources' not in st.session_state:
    st.session_state.resources = []
if 'findings' not in st.session_state:
    st.session_state.findings = []
if 'dependency_graph' not in st.session_state:
    st.session_state.dependency_graph = None
if 'summary_stats' not in st.session_state:
    st.session_state.summary_stats = {}


def main():
    """Main application"""
    st.title("☁️ StratusIQ")
    st.subheader("IaC-to-Fix Cloud Cost & Security Intelligence Platform")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["🔍 Scan", "📊 Findings", "🔗 Dependency Graph", "📄 Report"]
    )
    
    if page == "🔍 Scan":
        render_scan_page()
    elif page == "📊 Findings":
        render_findings_page()
    elif page == "🔗 Dependency Graph":
        render_graph_page()
    elif page == "📄 Report":
        render_report_page()


def render_scan_page():
    """Render scan configuration page"""
    st.header("Infrastructure Scan")
    
    scan_mode = st.radio(
        "Select Scan Mode",
        ["Terraform Plan JSON", "AWS Read-Only Scan"]
    )
    
    if scan_mode == "Terraform Plan JSON":
        render_terraform_scan()
    else:
        render_aws_scan()


def render_terraform_scan():
    """Render Terraform scan interface"""
    st.subheader("Upload Terraform Plan JSON")
    st.write("Generate a Terraform plan in JSON format:")
    st.code("terraform plan -out=tfplan\nterraform show -json tfplan > plan.json", language="bash")
    
    uploaded_file = st.file_uploader("Choose a Terraform plan JSON file", type=['json'])
    
    if uploaded_file is not None:
        try:
            plan_data = json.load(uploaded_file)
            
            if st.button("Analyze Infrastructure", type="primary"):
                with st.spinner("Parsing Terraform plan..."):
                    parser = TerraformParser()
                    resources = parser.parse_plan(plan_data)
                    st.session_state.resources = resources
                    
                    st.success(f"✅ Parsed {len(resources)} resources")
                    
                    # Run analysis
                    run_analysis(resources)
                    
        except Exception as e:
            st.error(f"Error parsing Terraform plan: {str(e)}")
            logger.error(f"Terraform parse error: {str(e)}")


def render_aws_scan():
    """Render AWS scan interface"""
    st.subheader("AWS Read-Only Scan")
    st.write("Scan your AWS infrastructure using read-only credentials")
    
    st.info("💡 Ensure your IAM credentials have read-only permissions. See the IAM policy example in the documentation.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        aws_region = st.selectbox(
            "AWS Region",
            ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"]
        )
    
    with col2:
        use_default_creds = st.checkbox("Use default AWS credentials", value=True)
    
    aws_access_key = None
    aws_secret_key = None
    
    if not use_default_creds:
        aws_access_key = st.text_input("AWS Access Key ID", type="password")
        aws_secret_key = st.text_input("AWS Secret Access Key", type="password")
    
    if st.button("Scan AWS Infrastructure", type="primary"):
        try:
            with st.spinner("Scanning AWS infrastructure..."):
                scanner = AWSScanner(region=aws_region)
                resources = scanner.scan_infrastructure(aws_access_key, aws_secret_key)
                st.session_state.resources = resources
                
                st.success(f"✅ Scanned {len(resources)} resources")
                log_scan_event("aws", len(resources))
                
                # Run analysis
                run_analysis(resources)
                
        except Exception as e:
            st.error(f"Error scanning AWS: {str(e)}")
            logger.error(f"AWS scan error: {str(e)}")
            st.info("Make sure your AWS credentials are configured correctly")


def run_analysis(resources):
    """Run full analysis pipeline"""
    with st.spinner("Building dependency graph..."):
        dep_graph = DependencyGraph()
        dep_graph.build_graph(resources)
        st.session_state.dependency_graph = dep_graph
    
    with st.spinner("Running detection rules..."):
        rule_engine = RuleEngine()
        findings = rule_engine.run_all_checks(resources, dep_graph)
    
    with st.spinner("Calculating priority scores..."):
        scorer = PriorityScorer()
        findings = scorer.score_findings(findings)
        summary_stats = scorer.get_summary_stats(findings)
        
        st.session_state.findings = findings
        st.session_state.summary_stats = summary_stats
    
    st.success("✅ Analysis complete!")
    
    # Show summary
    st.subheader("Analysis Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Findings", summary_stats.get('total_findings', 0))
    with col2:
        st.metric("Critical Issues", summary_stats.get('critical_findings', 0))
    with col3:
        st.metric("Monthly Savings", f"${summary_stats.get('total_monthly_savings', 0):,.2f}")
    with col4:
        st.metric("Annual Savings", f"${summary_stats.get('total_annual_savings', 0):,.2f}")
    
    # Category breakdown
    st.subheader("Findings Breakdown")
    col1, col2 = st.columns(2)
    
    with col1:
        # By category
        fig_category = go.Figure(data=[go.Pie(
            labels=['Cost', 'Security'],
            values=[summary_stats.get('cost_findings', 0), 
                   summary_stats.get('security_findings', 0)],
            hole=.3
        )])
        fig_category.update_layout(title="By Category", height=300)
        st.plotly_chart(fig_category, use_container_width=True)
    
    with col2:
        # By severity
        fig_severity = go.Figure(data=[go.Bar(
            x=['Critical', 'High', 'Medium', 'Low'],
            y=[summary_stats.get('critical_findings', 0),
               summary_stats.get('high_findings', 0),
               summary_stats.get('medium_findings', 0),
               summary_stats.get('low_findings', 0)],
            marker_color=['#ff4444', '#ff8844', '#ffbb44', '#44ff44']
        )])
        fig_severity.update_layout(title="By Severity", height=300)
        st.plotly_chart(fig_severity, use_container_width=True)


def render_findings_page():
    """Render findings page"""
    st.header("Findings")
    
    if not st.session_state.findings:
        st.info("No findings available. Please run a scan first.")
        return
    
    # Render findings table
    selected_finding, dep_graph = render_findings_table(
        st.session_state.findings,
        st.session_state.dependency_graph
    )
    
    # Render detail view if finding selected
    if selected_finding:
        st.divider()
        render_finding_detail(selected_finding, dep_graph)


def render_graph_page():
    """Render dependency graph page"""
    st.header("Resource Dependency Graph")
    
    if not st.session_state.dependency_graph:
        st.info("No graph data available. Please run a scan first.")
        return
    
    graph_data = st.session_state.dependency_graph.get_graph_data()
    render_graph_view(graph_data)


def render_report_page():
    """Render report generation page"""
    st.header("Generate Report")
    
    if not st.session_state.findings:
        st.info("No findings available. Please run a scan first.")
        return
    
    st.write("Generate a comprehensive PDF report of all findings")
    
    # Report options
    report_name = st.text_input("Report filename", value="stratusiq_report.pdf")
    
    if st.button("Generate PDF Report", type="primary"):
        try:
            with st.spinner("Generating report..."):
                generator = ReportGenerator()
                output_path = generator.generate_report(
                    st.session_state.findings,
                    st.session_state.summary_stats,
                    report_name
                )
            
            st.success(f"✅ Report generated: {output_path}")
            
            # Offer download
            with open(output_path, 'rb') as f:
                st.download_button(
                    label="📥 Download Report",
                    data=f,
                    file_name=report_name,
                    mime="application/pdf"
                )
                
        except Exception as e:
            st.error(f"Error generating report: {str(e)}")
            logger.error(f"Report generation error: {str(e)}")


if __name__ == "__main__":
    main()
