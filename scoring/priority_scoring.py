"""Priority scoring algorithm"""
from typing import Dict, List
import config
from utils.logging_utils import setup_logger

logger = setup_logger(__name__)


class PriorityScorer:
    """Calculate priority scores for findings"""
    
    def score_findings(self, findings: List[Dict]) -> List[Dict]:
        """Score and sort findings by priority"""
        for finding in findings:
            finding['priority_score'] = self._calculate_priority(finding)
        
        # Sort by priority score (descending)
        findings.sort(key=lambda x: x['priority_score'], reverse=True)
        
        logger.info(f"Scored {len(findings)} findings")
        return findings
    
    def _calculate_priority(self, finding: Dict) -> float:
        """Calculate priority score for a finding"""
        # Get severity score
        severity = finding.get('severity', 'low')
        severity_score = config.SEVERITY_SCORES.get(severity, 25)
        
        # Get cost savings
        cost_savings = finding.get('estimated_monthly_savings', 0)
        
        # Get change risk score
        change_risk = finding.get('change_risk', 'medium')
        risk_score = config.RISK_SCORES.get(change_risk, 30)
        
        # Apply additional penalty for high-risk changes (from impact simulation)
        impact_risk = finding.get('impact_risk_level', '')
        if impact_risk == 'High':
            risk_score += 20  # Additional penalty for high-risk changes
        
        # Calculate weighted priority score
        priority_score = (
            config.COST_SAVINGS_WEIGHT * cost_savings +
            config.SEVERITY_WEIGHT * severity_score -
            config.CHANGE_RISK_WEIGHT * risk_score
        )
        
        return round(priority_score, 2)
    
    def get_summary_stats(self, findings: List[Dict]) -> Dict:
        """Get summary statistics for findings"""
        total_findings = len(findings)
        
        # Count by category
        cost_findings = sum(1 for f in findings if f['category'] == 'cost')
        security_findings = sum(1 for f in findings if f['category'] == 'security')
        
        # Count by severity
        critical_findings = sum(1 for f in findings if f['severity'] == 'critical')
        high_findings = sum(1 for f in findings if f['severity'] == 'high')
        medium_findings = sum(1 for f in findings if f['severity'] == 'medium')
        low_findings = sum(1 for f in findings if f['severity'] == 'low')
        
        # Calculate total savings
        total_savings = sum(f.get('estimated_monthly_savings', 0) for f in findings)
        annual_savings = total_savings * 12
        
        return {
            "total_findings": total_findings,
            "cost_findings": cost_findings,
            "security_findings": security_findings,
            "critical_findings": critical_findings,
            "high_findings": high_findings,
            "medium_findings": medium_findings,
            "low_findings": low_findings,
            "total_monthly_savings": round(total_savings, 2),
            "total_annual_savings": round(annual_savings, 2)
        }
