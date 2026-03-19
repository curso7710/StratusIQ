"""LLM-based explanation engine for findings"""
import json
from typing import Dict
from utils.logging_utils import setup_logger

logger = setup_logger(__name__)


class ExplanationEngine:
    """Generate human-readable explanations for findings"""
    
    def explain_finding(self, finding: Dict) -> str:
        """
        Generate explanation for a finding using structured data only.
        This is a rule-based explanation engine that doesn't require LLM.
        In production, this could call an LLM API with the finding JSON.
        """
        category = finding.get('category')
        finding_id = finding.get('id', '')
        
        if category == 'cost':
            return self._explain_cost_finding(finding)
        elif category == 'security':
            return self._explain_security_finding(finding)
        else:
            return self._generic_explanation(finding)
    
    def _explain_cost_finding(self, finding: Dict) -> str:
        """Explain cost optimization finding"""
        finding_id = finding.get('id', '')
        evidence = finding.get('evidence', {})
        savings = finding.get('estimated_monthly_savings', 0)
        
        if 'idle-ec2' in finding_id:
            cpu = evidence.get('cpu_average', 0)
            instance_type = evidence.get('instance_type', 'unknown')
            return f"""**Why flagged:** This EC2 instance has an average CPU utilization of {cpu}% over the past 7 days, which is below the idle threshold of {evidence.get('threshold', 10)}%. This indicates the instance is underutilized.

**Cost impact:** Running this {instance_type} instance costs approximately ${savings:.2f} per month. If the instance is truly idle, this is wasted spend.

**What the fix does:** The recommended fix is to stop or terminate the instance. Stopping preserves the instance configuration and EBS volumes while eliminating compute charges. Terminating removes the instance entirely.

**Trade-offs:** 
- Stopping: You can restart the instance later, but you'll still pay for EBS storage
- Terminating: Eliminates all costs but requires recreating the instance if needed
- Consider if this is a development/test instance that can be stopped outside business hours"""
        
        elif 'overprov-ec2' in finding_id or 'large-low-util' in finding_id:
            cpu = evidence.get('cpu_average', 0)
            current = evidence.get('current_instance_type', 'unknown')
            suggested = evidence.get('suggested_instance_type', 'unknown')
            return f"""**Why flagged:** This EC2 instance has an average CPU utilization of {cpu}%, indicating it's overprovisioned for its workload. The current instance type ({current}) has more capacity than needed.

**Cost impact:** Downsizing from {current} to {suggested} would save approximately ${savings:.2f} per month while still providing adequate capacity.

**What the fix does:** The fix changes the instance type to a smaller size. This requires stopping the instance, modifying the instance type, and restarting it.

**Trade-offs:**
- Brief downtime required (typically 2-5 minutes)
- Performance may decrease slightly, but should still be adequate based on current utilization
- Monitor performance after the change to ensure it meets requirements
- Easy to rollback if needed"""
        
        elif 'unattached-ebs' in finding_id:
            size = evidence.get('size_gb', 0)
            return f"""**Why flagged:** This EBS volume is not attached to any EC2 instance. Unattached volumes still incur storage charges but provide no value.

**Cost impact:** This {size}GB volume costs approximately ${savings:.2f} per month. If it's not needed, this is wasted spend.

**What the fix does:** The recommended fix is to delete the volume after creating a snapshot for backup. Snapshots are cheaper than volumes and can be used to recreate the volume if needed.

**Trade-offs:**
- Snapshots cost less than volumes (${size * 0.05:.2f}/month vs ${savings:.2f}/month)
- Data is preserved in the snapshot
- Restoring from snapshot takes time if you need the volume again
- Verify the volume isn't needed before deletion"""
        
        elif 'unused-eip' in finding_id:
            public_ip = evidence.get('public_ip', 'unknown')
            return f"""**Why flagged:** This Elastic IP ({public_ip}) is allocated but not associated with any running instance. AWS charges for unassociated Elastic IPs.

**Cost impact:** Unused Elastic IPs cost ${savings:.2f} per month. This charge is eliminated when the IP is released or associated with an instance.

**What the fix does:** Release the Elastic IP to stop incurring charges.

**Trade-offs:**
- You'll lose this specific IP address
- If you need an Elastic IP later, you'll get a different address
- Consider if this IP is documented anywhere (DNS, firewall rules, etc.)
- No impact if the IP isn't actively used"""
        
        else:
            return self._generic_cost_explanation(finding)
    
    def _explain_security_finding(self, finding: Dict) -> str:
        """Explain security finding"""
        finding_id = finding.get('id', '')
        evidence = finding.get('evidence', {})
        severity = finding.get('severity', 'unknown')
        
        if 'open-sg' in finding_id:
            port = evidence.get('port', 'unknown')
            sg_id = evidence.get('security_group_id', 'unknown')
            return f"""**Why flagged:** Security group {sg_id} allows inbound traffic from the entire internet (0.0.0.0/0) on port {port}. This is a {severity} severity issue.

**Security impact:** Exposing port {port} to the internet significantly increases attack surface. Common attacks include:
- Port 22 (SSH): Brute force attacks, unauthorized access
- Port 3389 (RDP): Remote desktop attacks
- Port 3306/5432 (Database): Direct database access, data exfiltration

**What the fix does:** Restrict the security group to allow access only from trusted IP ranges (e.g., your corporate VPN, specific office IPs, or VPC CIDR).

**Trade-offs:**
- Improved security posture
- May require VPN or bastion host for access
- Need to maintain list of authorized IP addresses
- Test access after applying the fix to ensure legitimate users can still connect"""
        
        elif 'public-s3' in finding_id:
            bucket = evidence.get('bucket_name', 'unknown')
            return f"""**Why flagged:** S3 bucket {bucket} has public read access enabled, allowing anyone on the internet to list and download objects.

**Security impact:** This is a {severity} severity issue that can lead to:
- Data exposure and leaks
- Compliance violations (GDPR, HIPAA, etc.)
- Reputational damage
- Potential data exfiltration

**What the fix does:** Change the bucket ACL from public-read to private, restricting access to authorized AWS principals only.

**Trade-offs:**
- Improved security and compliance
- Applications/users will need proper IAM permissions to access the bucket
- May break existing integrations that rely on public access
- Test thoroughly before applying to production buckets"""
        
        elif 's3-no-block' in finding_id:
            bucket = evidence.get('bucket_name', 'unknown')
            return f"""**Why flagged:** S3 bucket {bucket} doesn't have public access block settings enabled. This is a defense-in-depth control that prevents accidental public exposure.

**Security impact:** Without public access block, it's easier to accidentally make the bucket public through ACLs or bucket policies. This is a {severity} severity issue.

**What the fix does:** Enable all four public access block settings:
- BlockPublicAcls: Prevents new public ACLs
- IgnorePublicAcls: Ignores existing public ACLs
- BlockPublicPolicy: Prevents public bucket policies
- RestrictPublicBuckets: Restricts cross-account access

**Trade-offs:**
- Strong protection against accidental public exposure
- No impact if bucket should be private
- May block legitimate public access if bucket is intentionally public (rare)
- Recommended for all buckets unless there's a specific need for public access"""
        
        elif 'ebs-unencrypted' in finding_id:
            volume_id = evidence.get('volume_id', 'unknown')
            size = evidence.get('size_gb', 0)
            return f"""**Why flagged:** EBS volume {volume_id} ({size}GB) is not encrypted. This is a {severity} severity issue for compliance and data protection.

**Security impact:** Unencrypted volumes expose data at rest:
- Data visible if volume is accessed outside normal channels
- Compliance violations (PCI-DSS, HIPAA require encryption)
- Snapshots are also unencrypted
- Data could be exposed if physical media is compromised

**What the fix does:** Create an encrypted copy of the volume. This requires:
1. Creating a snapshot
2. Copying the snapshot with encryption
3. Creating a new encrypted volume
4. Replacing the old volume with the new one

**Trade-offs:**
- Significant operational complexity (requires downtime)
- Must detach and reattach volume
- Minimal performance impact (encryption is hardware-accelerated)
- Cannot encrypt in-place, must create new volume
- Plan carefully and test in non-production first"""
        
        elif 'iam-wildcard' in finding_id:
            role_name = evidence.get('role_name', 'unknown')
            return f"""**Why flagged:** IAM role {role_name} has overly permissive policies with wildcard actions or resources. This is a {severity} severity issue.

**Security impact:** Wildcard permissions violate the principle of least privilege:
- Excessive permissions increase blast radius of compromised credentials
- Makes it harder to audit what actions are actually needed
- Compliance violations (SOC2, ISO 27001 require least privilege)
- Potential for privilege escalation

**What the fix does:** Replace wildcard permissions with specific actions and resources based on actual usage. Review CloudTrail logs to identify required permissions.

**Trade-offs:**
- Improved security posture
- Requires analysis of actual permission usage
- May break functionality if permissions are too restrictive
- Iterative process to find the right balance
- Use IAM Access Analyzer to help identify required permissions"""
        
        else:
            return self._generic_security_explanation(finding)
    
    def _generic_cost_explanation(self, finding: Dict) -> str:
        """Generic cost finding explanation"""
        savings = finding.get('estimated_monthly_savings', 0)
        return f"""**Why flagged:** This resource has been identified as a cost optimization opportunity.

**Cost impact:** Implementing the recommended fix could save approximately ${savings:.2f} per month (${savings * 12:.2f} annually).

**What the fix does:** Review the Terraform patch and CLI commands for specific remediation steps.

**Trade-offs:** Evaluate the business impact before applying changes. Consider testing in a non-production environment first."""
    
    def _generic_security_explanation(self, finding: Dict) -> str:
        """Generic security finding explanation"""
        severity = finding.get('severity', 'unknown')
        return f"""**Why flagged:** This resource has a {severity} severity security issue that should be addressed.

**Security impact:** This finding represents a potential security risk that could lead to unauthorized access, data exposure, or compliance violations.

**What the fix does:** Review the Terraform patch and CLI commands for specific remediation steps.

**Trade-offs:** Security fixes should be prioritized based on severity. Test changes in non-production environments first to ensure they don't break functionality."""
    
    def _generic_explanation(self, finding: Dict) -> str:
        """Generic explanation for unknown finding types"""
        return f"""**Finding:** {finding.get('title', 'Unknown')}

**Category:** {finding.get('category', 'unknown')}
**Severity:** {finding.get('severity', 'unknown')}

**Evidence:** {json.dumps(finding.get('evidence', {}), indent=2)}

Review the detailed finding information and remediation suggestions."""
