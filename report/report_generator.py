"""PDF report generator"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from typing import List, Dict
from datetime import datetime
from utils.helpers import format_currency
from utils.logging_utils import setup_logger

logger = setup_logger(__name__)


class ReportGenerator:
    """Generate PDF reports for findings"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
    
    def generate_report(self, findings: List[Dict], summary_stats: Dict, 
                       output_path: str = "stratusiq_report.pdf"):
        """Generate comprehensive PDF report"""
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=30
        )
        story.append(Paragraph("StratusIQ Cloud Analysis Report", title_style))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                              self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", self.styles['Heading2']))
        
        summary_data = [
            ["Metric", "Value"],
            ["Total Findings", str(summary_stats.get('total_findings', 0))],
            ["Critical Issues", str(summary_stats.get('critical_findings', 0))],
            ["High Severity", str(summary_stats.get('high_findings', 0))],
            ["Monthly Savings Potential", format_currency(summary_stats.get('total_monthly_savings', 0))],
            ["Annual Savings Potential", format_currency(summary_stats.get('total_annual_savings', 0))],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Top Findings
        story.append(Paragraph("Top Priority Findings", self.styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        
        top_findings = findings[:10]  # Top 10
        
        for i, finding in enumerate(top_findings, 1):
            story.append(Paragraph(f"{i}. {finding.get('title', 'Unknown')}", 
                                 self.styles['Heading3']))
            
            details = f"""
            <b>Category:</b> {finding.get('category', 'unknown').upper()}<br/>
            <b>Severity:</b> {finding.get('severity', 'unknown').upper()}<br/>
            <b>Monthly Savings:</b> {format_currency(finding.get('estimated_monthly_savings', 0))}<br/>
            <b>Priority Score:</b> {finding.get('priority_score', 0):.2f}<br/>
            """
            
            story.append(Paragraph(details, self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Build PDF
        doc.build(story)
        logger.info(f"Report generated: {output_path}")
        return output_path
