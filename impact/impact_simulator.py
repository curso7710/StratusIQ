"""Change impact simulator for predicting operational effects of remediation"""
from typing import Dict, List
from impact.risk_rules import RiskRules
from graph.dependency_graph import DependencyGraph
from utils.logging_utils import setup_logger

logger = setup_logger(__name__)


class ImpactSimulator:
    """Simulate the operational impact of applying remediation fixes"""
    
    def __init__(self):
        self.risk_rules = RiskRules()
    
    def simulate_change(self, finding: Dict, dependency_graph: DependencyGraph = None) -> Dict:
        """
        Simulate the impact of applying a fix for a finding
        
        Args:
            finding: Finding dictionary with id, evidence, affected_resources
            dependency_graph: Optional dependency graph for blast radius analysis
        
        Returns:
            Impact simulation dictionary with risk assessment and guidance
        """
        finding_id = finding.get('id', '')
        
        # Determine change type
        change_type = self.risk_rules.get_change_type(finding_id)
        
        # Get risk level
        risk_level = self.risk_rules.get_risk_level(change_type)
        
        # Get downtime information
        downtime_info = self.risk_rules.get_downtime_info(change_type)
        
        # Get affected services from dependency graph
        affected_services = self._get_affected_services(finding, dependency_graph)
        
        # Get blast radius
        blast_radius = self._get_blast_radius(finding, dependency_graph)
        
        # Generate safety checks
        safety_checks = self.risk_rules.get_safety_checks(change_type, finding)
        
        # Generate rollback steps
        rollback_steps = self.risk_rules.get_rollback_steps(change_type, finding)
        
        # Build impact simulation result
        impact = {
            "change_type": change_type,
            "risk_level": risk_level,
            "downtime_probability": downtime_info.get('probability', 'Unknown'),
            "estimated_downtime": downtime_info.get('estimated_downtime', 'Unknown'),
            "downtime_details": downtime_info.get('details', ''),
            "affected_services": affected_services,
            "blast_radius": blast_radius,
            "blast_radius_count": len(blast_radius),
            "safety_checks": safety_checks,
            "rollback_steps": rollback_steps,
            "recommendations": self._get_recommendations(change_type, risk_level, finding)
        }
        
        logger.info(f"Simulated impact for {finding_id}: {change_type} ({risk_level} risk)")
        
        return impact
    
    def _get_affected_services(self, finding: Dict, dependency_graph: DependencyGraph) -> List[str]:
        """Identify services affected by the change"""
        affected_services = []
        
        if not dependency_graph:
            return affected_services
        
        affected_resources = finding.get('affected_resources', [])
        
        for resource_id in affected_resources:
            # Get connected resources
            connected = dependency_graph.get_connected_resources(resource_id)
            
            # Map resource types to service names
            for conn_resource in connected:
                service_name = self._resource_to_service_name(conn_resource)
                if service_name and service_name not in affected_services:
                    affected_services.append(service_name)
        
        # Add the primary resource itself
        for resource_id in affected_resources:
            service_name = self._resource_to_service_name(resource_id)
            if service_name and service_name not in affected_services:
                affected_services.insert(0, service_name)
        
        return affected_services
    
    def _get_blast_radius(self, finding: Dict, dependency_graph: DependencyGraph) -> List[str]:
        """Get full blast radius from dependency graph"""
        if not dependency_graph:
            return finding.get('blast_radius', [])
        
        blast_radius = set()
        affected_resources = finding.get('affected_resources', [])
        
        for resource_id in affected_resources:
            # Get blast radius for this resource
            radius = dependency_graph.get_blast_radius(resource_id)
            blast_radius.update(radius)
        
        return list(blast_radius)
    
    def _resource_to_service_name(self, resource_id: str) -> str:
        """Convert resource ID to human-readable service name"""
        if not resource_id:
            return ""
        
        # Extract resource type and create friendly name
        if 'aws_instance' in resource_id or resource_id.startswith('i-'):
            return f"EC2 Instance ({resource_id.split('.')[-1]})"
        elif 'aws_security_group' in resource_id or resource_id.startswith('sg-'):
            return f"Security Group ({resource_id.split('.')[-1]})"
        elif 'aws_ebs_volume' in resource_id or resource_id.startswith('vol-'):
            return f"EBS Volume ({resource_id.split('.')[-1]})"
        elif 'aws_s3_bucket' in resource_id or resource_id.startswith('s3://'):
            bucket_name = resource_id.replace('s3://', '').split('.')[-1]
            return f"S3 Bucket ({bucket_name})"
        elif 'aws_iam_role' in resource_id or 'arn:aws:iam' in resource_id:
            role_name = resource_id.split('/')[-1] if '/' in resource_id else resource_id.split('.')[-1]
            return f"IAM Role ({role_name})"
        elif 'aws_eip' in resource_id or resource_id.startswith('eipalloc-'):
            return f"Elastic IP ({resource_id.split('.')[-1]})"
        elif 'subnet' in resource_id.lower():
            return f"VPC Subnet ({resource_id.split('.')[-1]})"
        elif 'vpc' in resource_id.lower():
            return f"VPC ({resource_id.split('.')[-1]})"
        elif 'alb' in resource_id.lower() or 'elb' in resource_id.lower():
            return f"Load Balancer ({resource_id.split('.')[-1]})"
        else:
            return resource_id
    
    def _get_recommendations(self, change_type: str, risk_level: str, finding: Dict) -> List[str]:
        """Generate recommendations based on change characteristics"""
        recommendations = []
        
        if risk_level == "High":
            recommendations.append("⚠️  HIGH RISK: Test this change in non-production environment first")
            recommendations.append("📋 Create detailed rollback plan before proceeding")
            recommendations.append("👥 Obtain approval from team lead or manager")
        
        if risk_level == "Medium":
            recommendations.append("⚡ MEDIUM RISK: Schedule during maintenance window if possible")
            recommendations.append("📊 Monitor metrics closely after applying change")
        
        if change_type == "REQUIRES_INSTANCE_RESTART":
            recommendations.append("🔄 Plan for brief service interruption during restart")
            recommendations.append("✅ Verify redundancy before proceeding")
        
        if change_type == "DESTRUCTIVE_CHANGE":
            recommendations.append("💾 CRITICAL: Create backup/snapshot before deletion")
            recommendations.append("⏰ Verify resource has been unused for sufficient time")
        
        if change_type == "NETWORK_POLICY_CHANGE":
            recommendations.append("🔒 Test connectivity from all required sources after change")
            recommendations.append("📝 Document original rules before modification")
        
        if change_type == "PERMISSION_CHANGE":
            recommendations.append("🔐 Use IAM Access Analyzer to validate required permissions")
            recommendations.append("📈 Review CloudTrail logs for actual permission usage")
        
        # Add cost-benefit recommendation
        savings = finding.get('estimated_monthly_savings', 0)
        if savings > 100:
            recommendations.append(f"💰 Potential savings: ${savings:.2f}/month (${savings*12:.2f}/year)")
        
        # Add security recommendation
        if finding.get('category') == 'security':
            severity = finding.get('severity', 'unknown')
            if severity in ['critical', 'high']:
                recommendations.append(f"🔴 {severity.upper()} security issue - prioritize remediation")
        
        return recommendations
    
    def get_change_complexity_score(self, impact: Dict) -> int:
        """
        Calculate complexity score (0-100) based on impact factors
        Higher score = more complex change
        """
        score = 0
        
        # Risk level contribution
        risk_level = impact.get('risk_level', 'Medium')
        if risk_level == 'High':
            score += 40
        elif risk_level == 'Medium':
            score += 20
        else:
            score += 5
        
        # Downtime contribution
        downtime_prob = impact.get('downtime_probability', 'None')
        if downtime_prob == 'Guaranteed':
            score += 30
        elif downtime_prob == 'Possible':
            score += 15
        
        # Blast radius contribution
        blast_radius_count = impact.get('blast_radius_count', 0)
        score += min(blast_radius_count * 2, 20)
        
        # Affected services contribution
        affected_count = len(impact.get('affected_services', []))
        score += min(affected_count * 3, 10)
        
        return min(score, 100)
