"""Main rule engine orchestrator"""
from typing import Dict, List
from engine.cost_rules import CostRules
from engine.security_rules import SecurityRules
from graph.dependency_graph import DependencyGraph
from utils.logging_utils import setup_logger

logger = setup_logger(__name__)


class RuleEngine:
    """Orchestrate all detection rules"""
    
    def __init__(self):
        self.cost_rules = CostRules()
        self.security_rules = SecurityRules()
        self.dependency_graph = None
    
    def run_all_checks(self, resources: List[Dict], 
                       dependency_graph: DependencyGraph = None) -> List[Dict]:
        """Run all detection rules"""
        self.dependency_graph = dependency_graph
        all_findings = []
        
        # Run cost checks
        logger.info("Running cost optimization checks...")
        all_findings.extend(self.cost_rules.check_idle_ec2_instances(resources))
        all_findings.extend(self.cost_rules.check_overprovisioned_ec2(resources))
        all_findings.extend(self.cost_rules.check_unattached_ebs_volumes(resources))
        all_findings.extend(self.cost_rules.check_unused_elastic_ips(resources))
        all_findings.extend(self.cost_rules.check_large_instances_low_utilization(resources))
        
        # Run security checks
        logger.info("Running security checks...")
        all_findings.extend(self.security_rules.check_open_security_groups(resources))
        all_findings.extend(self.security_rules.check_public_s3_buckets(resources))
        all_findings.extend(self.security_rules.check_s3_public_access_block(resources))
        all_findings.extend(self.security_rules.check_iam_wildcard_actions(resources))
        all_findings.extend(self.security_rules.check_iam_wildcard_resources(resources))
        all_findings.extend(self.security_rules.check_ebs_encryption(resources))
        
        # Enrich findings with blast radius
        if dependency_graph:
            all_findings = self._enrich_with_blast_radius(all_findings)
        
        logger.info(f"Found {len(all_findings)} total findings")
        return all_findings
    
    def _enrich_with_blast_radius(self, findings: List[Dict]) -> List[Dict]:
        """Add blast radius information to findings"""
        for finding in findings:
            affected_resources = finding.get('affected_resources', [])
            blast_radius = set()
            
            for resource_id in affected_resources:
                radius = self.dependency_graph.get_blast_radius(resource_id)
                blast_radius.update(radius)
            
            finding['blast_radius'] = list(blast_radius)
        
        return findings
