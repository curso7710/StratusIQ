"""Generate AWS CLI fix commands"""
from typing import Dict
from utils.logging_utils import setup_logger

logger = setup_logger(__name__)


class CLIFixGenerator:
    """Generate AWS CLI commands for findings"""
    
    def generate_cli_command(self, finding: Dict) -> str:
        """Generate AWS CLI command for a finding"""
        finding_id = finding.get('id', '')
        
        if 'idle-ec2' in finding_id:
            return self._cli_idle_ec2(finding)
        elif 'overprov-ec2' in finding_id or 'large-low-util' in finding_id:
            return self._cli_overprovisioned_ec2(finding)
        elif 'unattached-ebs' in finding_id:
            return self._cli_unattached_ebs(finding)
        elif 'unused-eip' in finding_id:
            return self._cli_unused_eip(finding)
        elif 'open-sg' in finding_id:
            return self._cli_open_security_group(finding)
        elif 'public-s3' in finding_id:
            return self._cli_public_s3(finding)
        elif 's3-no-block' in finding_id:
            return self._cli_s3_public_block(finding)
        elif 'ebs-unencrypted' in finding_id:
            return self._cli_ebs_encryption(finding)
        else:
            return "# Manual review required"
    
    def _cli_idle_ec2(self, finding: Dict) -> str:
        """Generate CLI for idle EC2 instance"""
        resource_id = finding['affected_resources'][0]
        instance_id = resource_id.split('.')[-1] if '.' in resource_id else resource_id
        
        return f"""# Stop idle EC2 instance
aws ec2 stop-instances --instance-ids {instance_id}

# Verify instance stopped
aws ec2 describe-instances --instance-ids {instance_id} --query 'Reservations[0].Instances[0].State.Name'

# Optional: Terminate instance (WARNING: Permanent)
# aws ec2 terminate-instances --instance-ids {instance_id}

# Rollback: Start instance
# aws ec2 start-instances --instance-ids {instance_id}"""
    
    def _cli_overprovisioned_ec2(self, finding: Dict) -> str:
        """Generate CLI for overprovisioned EC2"""
        resource_id = finding['affected_resources'][0]
        instance_id = resource_id.split('.')[-1] if '.' in resource_id else resource_id
        suggested_type = finding['evidence'].get('suggested_instance_type')
        current_type = finding['evidence'].get('current_instance_type')
        
        return f"""# Resize EC2 instance
# Step 1: Stop the instance
aws ec2 stop-instances --instance-ids {instance_id}

# Step 2: Wait for instance to stop
aws ec2 wait instance-stopped --instance-ids {instance_id}

# Step 3: Modify instance type
aws ec2 modify-instance-attribute \\
  --instance-id {instance_id} \\
  --instance-type {suggested_type}

# Step 4: Start the instance
aws ec2 start-instances --instance-ids {instance_id}

# Verify new instance type
aws ec2 describe-instances --instance-ids {instance_id} \\
  --query 'Reservations[0].Instances[0].InstanceType'

# Rollback: Change back to {current_type}
# aws ec2 stop-instances --instance-ids {instance_id}
# aws ec2 wait instance-stopped --instance-ids {instance_id}
# aws ec2 modify-instance-attribute --instance-id {instance_id} --instance-type {current_type}
# aws ec2 start-instances --instance-ids {instance_id}"""
    
    def _cli_unattached_ebs(self, finding: Dict) -> str:
        """Generate CLI for unattached EBS volume"""
        resource_id = finding['affected_resources'][0]
        volume_id = resource_id.split('.')[-1] if '.' in resource_id else resource_id
        
        return f"""# Delete unattached EBS volume
# Step 1: Create snapshot for backup
aws ec2 create-snapshot \\
  --volume-id {volume_id} \\
  --description "Backup before deletion"

# Step 2: Wait for snapshot to complete
# aws ec2 wait snapshot-completed --snapshot-ids <snapshot-id>

# Step 3: Delete the volume
aws ec2 delete-volume --volume-id {volume_id}

# Verify deletion
aws ec2 describe-volumes --volume-ids {volume_id}

# Rollback: Create volume from snapshot
# aws ec2 create-volume --snapshot-id <snapshot-id> --availability-zone <az>"""
    
    def _cli_unused_eip(self, finding: Dict) -> str:
        """Generate CLI for unused Elastic IP"""
        public_ip = finding['evidence'].get('public_ip')
        allocation_id = finding['affected_resources'][0]
        
        return f"""# Release unused Elastic IP
aws ec2 release-address --allocation-id {allocation_id}

# Verify release
aws ec2 describe-addresses --allocation-ids {allocation_id}

# Rollback: Allocate new EIP (will have different IP)
# aws ec2 allocate-address --domain vpc"""
    
    def _cli_open_security_group(self, finding: Dict) -> str:
        """Generate CLI for open security group"""
        sg_id = finding['evidence'].get('security_group_id')
        port = finding['evidence'].get('port')
        protocol = finding['evidence'].get('protocol', 'tcp')
        
        return f"""# Restrict security group access
# Step 1: Revoke public access
aws ec2 revoke-security-group-ingress \\
  --group-id {sg_id} \\
  --protocol {protocol} \\
  --port {port} \\
  --cidr 0.0.0.0/0

# Step 2: Add restricted access (replace with your CIDR)
aws ec2 authorize-security-group-ingress \\
  --group-id {sg_id} \\
  --protocol {protocol} \\
  --port {port} \\
  --cidr 10.0.0.0/8

# Verify changes
aws ec2 describe-security-groups --group-ids {sg_id}

# Rollback: Re-add public access (NOT RECOMMENDED)
# aws ec2 authorize-security-group-ingress --group-id {sg_id} --protocol {protocol} --port {port} --cidr 0.0.0.0/0"""
    
    def _cli_public_s3(self, finding: Dict) -> str:
        """Generate CLI for public S3 bucket"""
        bucket_name = finding['evidence'].get('bucket_name')
        
        return f"""# Remove public access from S3 bucket
# Step 1: Remove public ACL
aws s3api put-bucket-acl \\
  --bucket {bucket_name} \\
  --acl private

# Step 2: Verify ACL
aws s3api get-bucket-acl --bucket {bucket_name}

# Rollback: Make public again (NOT RECOMMENDED)
# aws s3api put-bucket-acl --bucket {bucket_name} --acl public-read"""
    
    def _cli_s3_public_block(self, finding: Dict) -> str:
        """Generate CLI for S3 public access block"""
        bucket_name = finding['evidence'].get('bucket_name')
        
        return f"""# Enable S3 public access block
aws s3api put-public-access-block \\
  --bucket {bucket_name} \\
  --public-access-block-configuration \\
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

# Verify configuration
aws s3api get-public-access-block --bucket {bucket_name}

# Rollback: Disable public access block (NOT RECOMMENDED)
# aws s3api put-public-access-block --bucket {bucket_name} --public-access-block-configuration "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false""""
    
    def _cli_ebs_encryption(self, finding: Dict) -> str:
        """Generate CLI for EBS encryption"""
        volume_id = finding['evidence'].get('volume_id')
        
        return f"""# Enable EBS encryption (requires volume replacement)
# Step 1: Create snapshot of existing volume
SNAPSHOT_ID=$(aws ec2 create-snapshot \\
  --volume-id {volume_id} \\
  --description "Snapshot for encryption" \\
  --query 'SnapshotId' --output text)

echo "Created snapshot: $SNAPSHOT_ID"

# Step 2: Wait for snapshot to complete
aws ec2 wait snapshot-completed --snapshot-ids $SNAPSHOT_ID

# Step 3: Copy snapshot with encryption
ENCRYPTED_SNAPSHOT=$(aws ec2 copy-snapshot \\
  --source-region us-east-1 \\
  --source-snapshot-id $SNAPSHOT_ID \\
  --encrypted \\
  --query 'SnapshotId' --output text)

echo "Created encrypted snapshot: $ENCRYPTED_SNAPSHOT"

# Step 4: Wait for encrypted snapshot
aws ec2 wait snapshot-completed --snapshot-ids $ENCRYPTED_SNAPSHOT

# Step 5: Create encrypted volume from snapshot
# Get availability zone first
AZ=$(aws ec2 describe-volumes --volume-ids {volume_id} --query 'Volumes[0].AvailabilityZone' --output text)

NEW_VOLUME=$(aws ec2 create-volume \\
  --snapshot-id $ENCRYPTED_SNAPSHOT \\
  --availability-zone $AZ \\
  --encrypted \\
  --query 'VolumeId' --output text)

echo "Created encrypted volume: $NEW_VOLUME"

# Step 6: Manual steps required:
# - Stop instance
# - Detach old volume
# - Attach new encrypted volume
# - Start instance
# - Verify and delete old volume

# Rollback: Reattach original volume {volume_id}"""
