"""Risk classification rules for change impact analysis"""
from typing import Dict, List
from utils.logging_utils import setup_logger

logger = setup_logger(__name__)


class RiskRules:
    """Define risk levels and change types for different operations"""
    
    # Change type classifications
    CHANGE_TYPES = {
        # EC2 changes
        "idle-ec2": "REQUIRES_INSTANCE_RESTART",
        "overprov-ec2": "REQUIRES_INSTANCE_RESTART",
        "large-low-util": "REQUIRES_INSTANCE_RESTART",
        
        # EBS changes
        "unattached-ebs": "DESTRUCTIVE_CHANGE",
        "ebs-unencrypted": "REQUIRES_VOLUME_REPLACEMENT",
        
        # Network changes
        "open-sg": "NETWORK_POLICY_CHANGE",
        
        # S3 changes
        "public-s3": "ACCESS_CONTROL_CHANGE",
        "s3-no-block": "ACCESS_CONTROL_CHANGE",
        
        # IAM changes
        "iam-wildcard": "PERMISSION_CHANGE",
        
        # EIP changes
        "unused-eip": "NETWORK_RESOURCE_DELETION",
    }
    
    # Risk level mappings
    RISK_LEVELS = {
        # Low risk - non-disruptive changes
        "ACCESS_CONTROL_CHANGE": "Low",
        "NETWORK_RESOURCE_DELETION": "Low",
        
        # Medium risk - requires restart or brief disruption
        "REQUIRES_INSTANCE_RESTART": "Medium",
        "NETWORK_POLICY_CHANGE": "Medium",
        "PERMISSION_CHANGE": "Medium",
        
        # High risk - destructive or complex changes
        "DESTRUCTIVE_CHANGE": "High",
        "REQUIRES_VOLUME_REPLACEMENT": "High",
    }
    
    # Downtime probability rules
    DOWNTIME_RULES = {
        "REQUIRES_INSTANCE_RESTART": {
            "probability": "Possible",
            "estimated_downtime": "1-2 minutes",
            "details": "Instance must be stopped and restarted"
        },
        "DESTRUCTIVE_CHANGE": {
            "probability": "None",
            "estimated_downtime": "0",
            "details": "Resource is not in use"
        },
        "NETWORK_POLICY_CHANGE": {
            "probability": "Possible",
            "estimated_downtime": "0-30 seconds",
            "details": "Brief connection interruption during rule propagation"
        },
        "ACCESS_CONTROL_CHANGE": {
            "probability": "None",
            "estimated_downtime": "0",
            "details": "Policy change is immediate and non-disruptive"
        },
        "PERMISSION_CHANGE": {
            "probability": "Possible",
            "estimated_downtime": "0",
            "details": "May cause authorization failures if too restrictive"
        },
        "NETWORK_RESOURCE_DELETION": {
            "probability": "None",
            "estimated_downtime": "0",
            "details": "Resource is not associated with running services"
        },
        "REQUIRES_VOLUME_REPLACEMENT": {
            "probability": "Guaranteed",
            "estimated_downtime": "5-15 minutes",
            "details": "Volume must be detached, replaced, and reattached"
        },
    }
    
    @staticmethod
    def get_change_type(finding_id: str) -> str:
        """Determine change type from finding ID"""
        for key, change_type in RiskRules.CHANGE_TYPES.items():
            if key in finding_id:
                return change_type
        return "CONFIGURATION_CHANGE"
    
    @staticmethod
    def get_risk_level(change_type: str) -> str:
        """Get risk level for change type"""
        return RiskRules.RISK_LEVELS.get(change_type, "Medium")
    
    @staticmethod
    def get_downtime_info(change_type: str) -> Dict:
        """Get downtime information for change type"""
        return RiskRules.DOWNTIME_RULES.get(change_type, {
            "probability": "Unknown",
            "estimated_downtime": "Unknown",
            "details": "Manual assessment required"
        })
    
    @staticmethod
    def get_safety_checks(change_type: str, finding: Dict) -> List[str]:
        """Generate safety checklist for change type"""
        checks = []
        
        if change_type == "REQUIRES_INSTANCE_RESTART":
            checks = [
                "✓ Verify instance is not a single point of failure",
                "✓ Check if instance is part of an Auto Scaling group",
                "✓ Confirm load balancer health checks are configured",
                "✓ Verify backup instances are available",
                "✓ Schedule change during maintenance window or low-traffic period",
                "✓ Notify dependent teams of planned downtime",
                "✓ Test application startup after restart",
                "✓ Monitor CloudWatch metrics post-change"
            ]
        
        elif change_type == "NETWORK_POLICY_CHANGE":
            checks = [
                "✓ Document current security group rules",
                "✓ Verify required application ports",
                "✓ Confirm internal service communication paths",
                "✓ Check if any automation depends on current access",
                "✓ Test connectivity from allowed sources",
                "✓ Ensure monitoring/logging access is maintained",
                "✓ Have rollback plan ready",
                "✓ Notify security team of changes"
            ]
        
        elif change_type == "DESTRUCTIVE_CHANGE":
            checks = [
                "✓ Create snapshot or backup before deletion",
                "✓ Verify resource is truly unused (check CloudWatch metrics)",
                "✓ Confirm no automation references this resource",
                "✓ Check for any tags indicating importance",
                "✓ Review resource creation date and history",
                "✓ Obtain approval from resource owner",
                "✓ Document deletion in change log",
                "✓ Set snapshot retention policy"
            ]
        
        elif change_type == "ACCESS_CONTROL_CHANGE":
            checks = [
                "✓ Review current bucket access patterns (S3 access logs)",
                "✓ Identify all applications accessing the bucket",
                "✓ Verify IAM policies grant necessary access",
                "✓ Test application access after change",
                "✓ Update bucket policies if needed",
                "✓ Check for any public-facing integrations",
                "✓ Notify application teams of access changes",
                "✓ Monitor for access denied errors"
            ]
        
        elif change_type == "PERMISSION_CHANGE":
            checks = [
                "✓ Review CloudTrail logs for actual permission usage",
                "✓ Use IAM Access Analyzer to identify required permissions",
                "✓ Test with restricted permissions in non-production",
                "✓ Identify all services/applications using this role",
                "✓ Have rollback plan ready",
                "✓ Monitor for authorization failures",
                "✓ Implement changes incrementally",
                "✓ Document permission changes"
            ]
        
        elif change_type == "REQUIRES_VOLUME_REPLACEMENT":
            checks = [
                "✓ Create snapshot of existing volume",
                "✓ Verify snapshot completed successfully",
                "✓ Stop instance before volume operations",
                "✓ Document volume attachment details (device name, etc.)",
                "✓ Test encrypted volume in non-production first",
                "✓ Verify application can access encrypted volume",
                "✓ Plan for extended downtime (5-15 minutes)",
                "✓ Keep original volume until verification complete"
            ]
        
        else:
            checks = [
                "✓ Review change in non-production environment first",
                "✓ Document current configuration",
                "✓ Identify affected services and dependencies",
                "✓ Prepare rollback plan",
                "✓ Schedule change during maintenance window",
                "✓ Monitor for issues post-change"
            ]
        
        return checks
    
    @staticmethod
    def get_rollback_steps(change_type: str, finding: Dict) -> List[str]:
        """Generate rollback instructions for change type"""
        steps = []
        
        if change_type == "REQUIRES_INSTANCE_RESTART":
            current_type = finding.get('evidence', {}).get('current_instance_type', 'unknown')
            resource_id = finding.get('affected_resources', ['unknown'])[0]
            
            steps = [
                "Rollback Steps:",
                "",
                "Option 1 - Terraform:",
                f"1. Revert instance_type to '{current_type}' in your .tf file",
                "2. Run: terraform plan",
                "3. Run: terraform apply",
                "",
                "Option 2 - AWS CLI:",
                f"1. Stop instance: aws ec2 stop-instances --instance-ids {resource_id}",
                "2. Wait for stopped state: aws ec2 wait instance-stopped --instance-ids {resource_id}",
                f"3. Modify type: aws ec2 modify-instance-attribute --instance-id {resource_id} --instance-type {current_type}",
                f"4. Start instance: aws ec2 start-instances --instance-ids {resource_id}",
                "",
                "Verification:",
                f"aws ec2 describe-instances --instance-ids {resource_id} --query 'Reservations[0].Instances[0].InstanceType'"
            ]
        
        elif change_type == "NETWORK_POLICY_CHANGE":
            sg_id = finding.get('evidence', {}).get('security_group_id', 'unknown')
            port = finding.get('evidence', {}).get('port', 'unknown')
            
            steps = [
                "Rollback Steps:",
                "",
                "AWS CLI:",
                f"1. Re-add the original rule:",
                f"   aws ec2 authorize-security-group-ingress \\",
                f"     --group-id {sg_id} \\",
                f"     --protocol tcp \\",
                f"     --port {port} \\",
                f"     --cidr 0.0.0.0/0",
                "",
                "Terraform:",
                "1. Revert the ingress rule in your .tf file",
                "2. Run: terraform apply",
                "",
                "Note: Original rule allowed 0.0.0.0/0 (not recommended for production)"
            ]
        
        elif change_type == "DESTRUCTIVE_CHANGE":
            resource_id = finding.get('affected_resources', ['unknown'])[0]
            
            steps = [
                "Rollback Steps:",
                "",
                "If snapshot was created:",
                "1. Identify snapshot ID from backup",
                f"2. Create volume: aws ec2 create-volume --snapshot-id <snapshot-id> --availability-zone <az>",
                "3. Wait for volume creation",
                "4. Attach to instance if needed",
                "",
                "If no snapshot:",
                "⚠️  Resource cannot be recovered",
                "   This is why creating snapshots before deletion is critical",
                "",
                "Prevention:",
                "Always create snapshots before deleting volumes"
            ]
        
        elif change_type == "ACCESS_CONTROL_CHANGE":
            bucket_name = finding.get('evidence', {}).get('bucket_name', 'unknown')
            
            steps = [
                "Rollback Steps:",
                "",
                "To restore public access (NOT RECOMMENDED):",
                f"aws s3api put-bucket-acl --bucket {bucket_name} --acl public-read",
                "",
                "To restore specific ACL:",
                "1. If you documented the original ACL, restore it",
                "2. Otherwise, use private ACL and grant specific permissions",
                "",
                "Note: Public buckets are a security risk. Consider alternatives:",
                "- CloudFront distribution with OAI",
                "- Pre-signed URLs for temporary access",
                "- Bucket policies with specific principals"
            ]
        
        elif change_type == "PERMISSION_CHANGE":
            role_name = finding.get('evidence', {}).get('role_name', 'unknown')
            
            steps = [
                "Rollback Steps:",
                "",
                "1. Identify the original policy ARN",
                "2. Re-attach the policy:",
                f"   aws iam attach-role-policy \\",
                f"     --role-name {role_name} \\",
                f"     --policy-arn <original-policy-arn>",
                "",
                "3. Verify:",
                f"   aws iam list-attached-role-policies --role-name {role_name}",
                "",
                "Best Practice:",
                "- Document current policies before changes",
                "- Use version control for IAM policies",
                "- Test permission changes in non-production first"
            ]
        
        else:
            steps = [
                "Rollback Steps:",
                "",
                "1. Revert configuration changes in Terraform",
                "2. Run: terraform plan (review changes)",
                "3. Run: terraform apply",
                "",
                "Or use AWS CLI to manually revert changes",
                "",
                "Always document original configuration before changes"
            ]
        
        return steps
