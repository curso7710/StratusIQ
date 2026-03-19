"""Security detection rules"""
from typing import Dict, List
import config
from utils.logging_utils import setup_logger

logger = setup_logger(__name__)


class SecurityRules:
    """Security vulnerability detection rules"""
    
    def __init__(self):
        self.findings = []
    
    def check_open_security_groups(self, resources: List[Dict]) -> List[Dict]:
        """Check for security groups open to 0.0.0.0/0 on risky ports"""
        findings = []
        
        for resource in resources:
            if resource['type'] != 'aws_security_group':
                continue
            
            ingress_rules = resource['config'].get('ingress', [])
            
            for rule in ingress_rules:
                ip_ranges = rule.get('IpRanges', [])
                from_port = rule.get('FromPort')
                to_port = rule.get('ToPort')
                
                # Check if open to internet
                open_to_internet = any(
                    ip_range.get('CidrIp') == '0.0.0.0/0' 
                    for ip_range in ip_ranges
                )
                
                if open_to_internet and from_port in config.RISKY_PORTS:
                    severity = "critical" if from_port in [22, 3389] else "high"
                    
                    finding = {
                        "id": f"sec-open-sg-{resource['resource_id']}-{from_port}",
                        "title": f"Security Group Open to Internet on Port {from_port}",
                        "category": "security",
                        "severity": severity,
                        "estimated_monthly_savings": 0,
                        "evidence": {
                            "security_group_id": resource['resource_id'],
                            "port": from_port,
                            "protocol": rule.get('IpProtocol', 'tcp'),
                            "cidr": "0.0.0.0/0"
                        },
                        "affected_resources": [resource['resource_id']],
                        "blast_radius": [],
                        "confidence": "high",
                        "change_risk": "medium"
                    }
                    findings.append(finding)
        
        return findings
    
    def check_public_s3_buckets(self, resources: List[Dict]) -> List[Dict]:
        """Check for public S3 buckets"""
        findings = []
        
        for resource in resources:
            if resource['type'] != 'aws_s3_bucket':
                continue
            
            acl_grants = resource['config'].get('acl_grants', [])
            
            # Check for public grants
            for grant in acl_grants:
                grantee = grant.get('Grantee', {})
                grantee_type = grantee.get('Type')
                uri = grantee.get('URI', '')
                
                if grantee_type == 'Group' and 'AllUsers' in uri:
                    finding = {
                        "id": f"sec-public-s3-{resource['resource_id']}",
                        "title": f"Public S3 Bucket: {resource['resource_id']}",
                        "category": "security",
                        "severity": "critical",
                        "estimated_monthly_savings": 0,
                        "evidence": {
                            "bucket_name": resource['resource_id'],
                            "public_access": True,
                            "permission": grant.get('Permission')
                        },
                        "affected_resources": [resource['resource_id']],
                        "blast_radius": [],
                        "confidence": "high",
                        "change_risk": "high"
                    }
                    findings.append(finding)
                    break
        
        return findings
    
    def check_s3_public_access_block(self, resources: List[Dict]) -> List[Dict]:
        """Check for missing S3 public access block"""
        findings = []
        
        for resource in resources:
            if resource['type'] != 'aws_s3_bucket':
                continue
            
            public_block = resource['config'].get('public_access_block', {})
            
            # Check if all settings are enabled
            block_public_acls = public_block.get('BlockPublicAcls', False)
            ignore_public_acls = public_block.get('IgnorePublicAcls', False)
            block_public_policy = public_block.get('BlockPublicPolicy', False)
            restrict_public_buckets = public_block.get('RestrictPublicBuckets', False)
            
            if not all([block_public_acls, ignore_public_acls, 
                       block_public_policy, restrict_public_buckets]):
                finding = {
                    "id": f"sec-s3-no-block-{resource['resource_id']}",
                    "title": f"S3 Bucket Missing Public Access Block: {resource['resource_id']}",
                    "category": "security",
                    "severity": "high",
                    "estimated_monthly_savings": 0,
                    "evidence": {
                        "bucket_name": resource['resource_id'],
                        "block_public_acls": block_public_acls,
                        "ignore_public_acls": ignore_public_acls,
                        "block_public_policy": block_public_policy,
                        "restrict_public_buckets": restrict_public_buckets
                    },
                    "affected_resources": [resource['resource_id']],
                    "blast_radius": [],
                    "confidence": "high",
                    "change_risk": "low"
                }
                findings.append(finding)
        
        return findings
    
    def check_iam_wildcard_actions(self, resources: List[Dict]) -> List[Dict]:
        """Check for IAM policies with wildcard actions"""
        findings = []
        
        for resource in resources:
            if resource['type'] != 'aws_iam_role':
                continue
            
            policies = resource['config'].get('attached_policies', [])
            
            for policy in policies:
                policy_name = policy.get('PolicyName', '')
                
                # Check for overly permissive policy names
                if '*' in policy_name or 'Admin' in policy_name or 'Full' in policy_name:
                    finding = {
                        "id": f"sec-iam-wildcard-action-{resource['resource_id']}",
                        "title": f"IAM Role with Overly Permissive Policy: {resource['config']['role_name']}",
                        "category": "security",
                        "severity": "high",
                        "estimated_monthly_savings": 0,
                        "evidence": {
                            "role_name": resource['config']['role_name'],
                            "policy_name": policy_name,
                            "policy_arn": policy.get('PolicyArn')
                        },
                        "affected_resources": [resource['resource_id']],
                        "blast_radius": [],
                        "confidence": "medium",
                        "change_risk": "high"
                    }
                    findings.append(finding)
                    break
        
        return findings
    
    def check_iam_wildcard_resources(self, resources: List[Dict]) -> List[Dict]:
        """Check for IAM policies with wildcard resources"""
        findings = []
        
        for resource in resources:
            if resource['type'] != 'aws_iam_role':
                continue
            
            assume_policy = resource['config'].get('assume_role_policy', {})
            
            # Check assume role policy for wildcards
            if isinstance(assume_policy, dict):
                statements = assume_policy.get('Statement', [])
                for statement in statements:
                    if isinstance(statement, dict):
                        principal = statement.get('Principal', {})
                        if principal == '*' or (isinstance(principal, dict) and '*' in str(principal)):
                            finding = {
                                "id": f"sec-iam-wildcard-resource-{resource['resource_id']}",
                                "title": f"IAM Role with Wildcard Principal: {resource['config']['role_name']}",
                                "category": "security",
                                "severity": "critical",
                                "estimated_monthly_savings": 0,
                                "evidence": {
                                    "role_name": resource['config']['role_name'],
                                    "principal": str(principal)
                                },
                                "affected_resources": [resource['resource_id']],
                                "blast_radius": [],
                                "confidence": "high",
                                "change_risk": "high"
                            }
                            findings.append(finding)
                            break
        
        return findings
    
    def check_ebs_encryption(self, resources: List[Dict]) -> List[Dict]:
        """Check for unencrypted EBS volumes"""
        findings = []
        
        for resource in resources:
            if resource['type'] != 'aws_ebs_volume':
                continue
            
            encrypted = resource['config'].get('encrypted', False)
            
            if not encrypted:
                finding = {
                    "id": f"sec-ebs-unencrypted-{resource['resource_id']}",
                    "title": f"Unencrypted EBS Volume: {resource['resource_id']}",
                    "category": "security",
                    "severity": "medium",
                    "estimated_monthly_savings": 0,
                    "evidence": {
                        "volume_id": resource['resource_id'],
                        "encrypted": False,
                        "size_gb": resource['config'].get('size')
                    },
                    "affected_resources": [resource['resource_id']],
                    "blast_radius": [],
                    "confidence": "high",
                    "change_risk": "high"
                }
                findings.append(finding)
        
        return findings
    
    def check_cloudtrail_enabled(self, resources: List[Dict]) -> List[Dict]:
        """Check if CloudTrail is enabled (placeholder)"""
        # This would require CloudTrail API calls
        # Placeholder for completeness
        return []
    
    def check_old_iam_keys(self, resources: List[Dict]) -> List[Dict]:
        """Check for old IAM access keys (placeholder)"""
        # This would require IAM access key age data
        # Placeholder for completeness
        return []
