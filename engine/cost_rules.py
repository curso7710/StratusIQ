"""Cost optimization detection rules"""
from typing import Dict, List
import config
from utils.logging_utils import setup_logger

logger = setup_logger(__name__)


class CostRules:
    """Cost optimization detection rules"""
    
    def __init__(self):
        self.findings = []
    
    def check_idle_ec2_instances(self, resources: List[Dict]) -> List[Dict]:
        """Check for idle EC2 instances (CPU < 10%)"""
        findings = []
        
        for resource in resources:
            if resource['type'] != 'aws_instance':
                continue
            
            cpu_avg = resource.get('metrics', {}).get('cpu_average', 0)
            instance_type = resource['config'].get('instance_type', '')
            state = resource['config'].get('state', '')
            
            if state == 'running' and cpu_avg < config.IDLE_CPU_THRESHOLD:
                monthly_cost = config.EC2_PRICING.get(instance_type, 50)
                
                finding = {
                    "id": f"cost-idle-ec2-{resource['resource_id']}",
                    "title": f"Idle EC2 Instance: {resource['resource_id']}",
                    "category": "cost",
                    "severity": "medium",
                    "estimated_monthly_savings": monthly_cost,
                    "evidence": {
                        "cpu_average": cpu_avg,
                        "instance_type": instance_type,
                        "threshold": config.IDLE_CPU_THRESHOLD
                    },
                    "affected_resources": [resource['resource_id']],
                    "blast_radius": [],
                    "confidence": "high",
                    "change_risk": "low"
                }
                findings.append(finding)
        
        return findings
    
    def check_overprovisioned_ec2(self, resources: List[Dict]) -> List[Dict]:
        """Check for overprovisioned EC2 instances (CPU < 30%)"""
        findings = []
        
        for resource in resources:
            if resource['type'] != 'aws_instance':
                continue
            
            cpu_avg = resource.get('metrics', {}).get('cpu_average', 0)
            instance_type = resource['config'].get('instance_type', '')
            state = resource['config'].get('state', '')
            
            if (state == 'running' and 
                config.IDLE_CPU_THRESHOLD <= cpu_avg < config.LOW_CPU_THRESHOLD):
                
                # Suggest downgrade
                current_cost = config.EC2_PRICING.get(instance_type, 50)
                suggested_type = self._suggest_smaller_instance(instance_type)
                suggested_cost = config.EC2_PRICING.get(suggested_type, 25)
                savings = current_cost - suggested_cost
                
                finding = {
                    "id": f"cost-overprov-ec2-{resource['resource_id']}",
                    "title": f"Overprovisioned EC2: {resource['resource_id']}",
                    "category": "cost",
                    "severity": "low",
                    "estimated_monthly_savings": savings,
                    "evidence": {
                        "cpu_average": cpu_avg,
                        "current_instance_type": instance_type,
                        "suggested_instance_type": suggested_type,
                        "threshold": config.LOW_CPU_THRESHOLD
                    },
                    "affected_resources": [resource['resource_id']],
                    "blast_radius": [],
                    "confidence": "medium",
                    "change_risk": "medium"
                }
                findings.append(finding)
        
        return findings
    
    def check_unattached_ebs_volumes(self, resources: List[Dict]) -> List[Dict]:
        """Check for unattached EBS volumes"""
        findings = []
        
        for resource in resources:
            if resource['type'] != 'aws_ebs_volume':
                continue
            
            attachments = resource['config'].get('attachments', [])
            state = resource['config'].get('state', '')
            size = resource['config'].get('size', 0)
            
            if state == 'available' or len(attachments) == 0:
                monthly_cost = size * config.EBS_PRICING_PER_GB
                
                finding = {
                    "id": f"cost-unattached-ebs-{resource['resource_id']}",
                    "title": f"Unattached EBS Volume: {resource['resource_id']}",
                    "category": "cost",
                    "severity": "low",
                    "estimated_monthly_savings": monthly_cost,
                    "evidence": {
                        "state": state,
                        "size_gb": size,
                        "attachments": len(attachments)
                    },
                    "affected_resources": [resource['resource_id']],
                    "blast_radius": [],
                    "confidence": "high",
                    "change_risk": "low"
                }
                findings.append(finding)
        
        return findings
    
    def check_unused_elastic_ips(self, resources: List[Dict]) -> List[Dict]:
        """Check for unused Elastic IPs"""
        findings = []
        
        for resource in resources:
            if resource['type'] != 'aws_eip':
                continue
            
            association_id = resource['config'].get('association_id')
            instance_id = resource['config'].get('instance_id')
            
            if not association_id and not instance_id:
                finding = {
                    "id": f"cost-unused-eip-{resource['resource_id']}",
                    "title": f"Unused Elastic IP: {resource['resource_id']}",
                    "category": "cost",
                    "severity": "low",
                    "estimated_monthly_savings": config.ELASTIC_IP_PRICING,
                    "evidence": {
                        "public_ip": resource['config'].get('public_ip'),
                        "associated": False
                    },
                    "affected_resources": [resource['resource_id']],
                    "blast_radius": [],
                    "confidence": "high",
                    "change_risk": "low"
                }
                findings.append(finding)
        
        return findings
    
    def check_large_instances_low_utilization(self, resources: List[Dict]) -> List[Dict]:
        """Check for large instance types with low utilization"""
        findings = []
        large_instance_families = ['m5.2xlarge', 'm5.4xlarge', 'c5.2xlarge', 
                                   'r5.2xlarge', 'r5.4xlarge']
        
        for resource in resources:
            if resource['type'] != 'aws_instance':
                continue
            
            instance_type = resource['config'].get('instance_type', '')
            cpu_avg = resource.get('metrics', {}).get('cpu_average', 0)
            state = resource['config'].get('state', '')
            
            if (state == 'running' and 
                any(family in instance_type for family in large_instance_families) and
                cpu_avg < config.LOW_CPU_THRESHOLD):
                
                current_cost = config.EC2_PRICING.get(instance_type, 100)
                suggested_type = self._suggest_smaller_instance(instance_type)
                suggested_cost = config.EC2_PRICING.get(suggested_type, 50)
                savings = current_cost - suggested_cost
                
                finding = {
                    "id": f"cost-large-low-util-{resource['resource_id']}",
                    "title": f"Large Instance with Low Utilization: {resource['resource_id']}",
                    "category": "cost",
                    "severity": "medium",
                    "estimated_monthly_savings": savings,
                    "evidence": {
                        "cpu_average": cpu_avg,
                        "current_instance_type": instance_type,
                        "suggested_instance_type": suggested_type
                    },
                    "affected_resources": [resource['resource_id']],
                    "blast_radius": [],
                    "confidence": "high",
                    "change_risk": "medium"
                }
                findings.append(finding)
        
        return findings
    
    def check_old_snapshots(self, resources: List[Dict]) -> List[Dict]:
        """Check for old EBS snapshots (placeholder - would need snapshot data)"""
        # This would require snapshot age data from AWS
        # Placeholder for completeness
        return []
    
    def _suggest_smaller_instance(self, current_type: str) -> str:
        """Suggest a smaller instance type"""
        downgrade_map = {
            'm5.4xlarge': 'm5.2xlarge',
            'm5.2xlarge': 'm5.xlarge',
            'm5.xlarge': 'm5.large',
            'm5.large': 't3.large',
            'c5.2xlarge': 'c5.xlarge',
            'c5.xlarge': 'c5.large',
            'r5.2xlarge': 'r5.xlarge',
            'r5.xlarge': 'r5.large',
        }
        return downgrade_map.get(current_type, 't3.medium')
