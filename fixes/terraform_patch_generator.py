"""Generate Terraform patch suggestions"""
from typing import Dict
from utils.logging_utils import setup_logger

logger = setup_logger(__name__)


class TerraformPatchGenerator:
    """Generate Terraform patches for findings"""
    
    def generate_patch(self, finding: Dict) -> str:
        """Generate Terraform patch for a finding"""
        finding_id = finding.get('id', '')
        
        if 'idle-ec2' in finding_id:
            return self._patch_idle_ec2(finding)
        elif 'overprov-ec2' in finding_id or 'large-low-util' in finding_id:
            return self._patch_overprovisioned_ec2(finding)
        elif 'unattached-ebs' in finding_id:
            return self._patch_unattached_ebs(finding)
        elif 'unused-eip' in finding_id:
            return self._patch_unused_eip(finding)
        elif 'open-sg' in finding_id:
            return self._patch_open_security_group(finding)
        elif 'public-s3' in finding_id:
            return self._patch_public_s3(finding)
        elif 's3-no-block' in finding_id:
            return self._patch_s3_public_block(finding)
        elif 'ebs-unencrypted' in finding_id:
            return self._patch_ebs_encryption(finding)
        else:
            return "# Manual review required"
    
    def _patch_idle_ec2(self, finding: Dict) -> str:
        """Generate patch for idle EC2 instance"""
        resource_id = finding['affected_resources'][0]
        
        return f"""# Terminate idle EC2 instance
# Resource: {resource_id}

# Option 1: Stop the instance (preserves data)
resource "aws_instance" "{resource_id}" {{
  # ... existing configuration ...
  
  # Add lifecycle to prevent accidental termination
  lifecycle {{
    prevent_destroy = true
  }}
}}

# Option 2: Remove the resource block entirely to destroy
# (Make sure to backup any data first)

# Rollback: Restart the instance if needed
# terraform apply with the original configuration"""
    
    def _patch_overprovisioned_ec2(self, finding: Dict) -> str:
        """Generate patch for overprovisioned EC2"""
        resource_id = finding['affected_resources'][0]
        current_type = finding['evidence'].get('current_instance_type')
        suggested_type = finding['evidence'].get('suggested_instance_type')
        
        return f"""# Downsize overprovisioned EC2 instance
# Resource: {resource_id}

resource "aws_instance" "{resource_id}" {{
  # ... existing configuration ...
  
- instance_type = "{current_type}"
+ instance_type = "{suggested_type}"
}}

# Apply with:
# terraform plan
# terraform apply

# Rollback:
# Change instance_type back to "{current_type}" """
    
    def _patch_unattached_ebs(self, finding: Dict) -> str:
        """Generate patch for unattached EBS volume"""
        resource_id = finding['affected_resources'][0]
        
        return f"""# Remove unattached EBS volume
# Resource: {resource_id}

# Option 1: Create snapshot before deletion
resource "aws_ebs_snapshot" "{resource_id}_backup" {{
  volume_id = aws_ebs_volume.{resource_id}.id
  description = "Backup before deletion"
}}

# Option 2: Remove the volume resource
# (Comment out or delete the resource block)

# resource "aws_ebs_volume" "{resource_id}" {{
#   ... existing configuration ...
# }}

# Rollback: Restore from snapshot if needed"""
    
    def _patch_unused_eip(self, finding: Dict) -> str:
        """Generate patch for unused Elastic IP"""
        resource_id = finding['affected_resources'][0]
        
        return f"""# Release unused Elastic IP
# Resource: {resource_id}

# Remove the Elastic IP resource
# (Comment out or delete the resource block)

# resource "aws_eip" "{resource_id}" {{
#   ... existing configuration ...
# }}

# Rollback: Allocate a new EIP if needed
# (Note: You'll get a different IP address)"""
    
    def _patch_open_security_group(self, finding: Dict) -> str:
        """Generate patch for open security group"""
        sg_id = finding['evidence'].get('security_group_id')
        port = finding['evidence'].get('port')
        
        return f"""# Restrict security group access
# Security Group: {sg_id}
# Port: {port}

resource "aws_security_group" "example" {{
  # ... existing configuration ...
  
  ingress {{
-   cidr_blocks = ["0.0.0.0/0"]
+   cidr_blocks = ["10.0.0.0/8"]  # Replace with your VPC CIDR or specific IPs
    from_port   = {port}
    to_port     = {port}
    protocol    = "tcp"
  }}
}}

# Rollback: Change cidr_blocks back to ["0.0.0.0/0"]
# (Not recommended for production)"""
    
    def _patch_public_s3(self, finding: Dict) -> str:
        """Generate patch for public S3 bucket"""
        bucket_name = finding['evidence'].get('bucket_name')
        
        return f"""# Remove public access from S3 bucket
# Bucket: {bucket_name}

resource "aws_s3_bucket_acl" "{bucket_name}" {{
  bucket = aws_s3_bucket.{bucket_name}.id
- acl    = "public-read"
+ acl    = "private"
}}

# Rollback: Change acl back to "public-read"
# (Not recommended for production)"""
    
    def _patch_s3_public_block(self, finding: Dict) -> str:
        """Generate patch for S3 public access block"""
        bucket_name = finding['evidence'].get('bucket_name')
        
        return f"""# Enable S3 public access block
# Bucket: {bucket_name}

resource "aws_s3_bucket_public_access_block" "{bucket_name}" {{
  bucket = aws_s3_bucket.{bucket_name}.id

+ block_public_acls       = true
+ block_public_policy     = true
+ ignore_public_acls      = true
+ restrict_public_buckets = true
}}

# Rollback: Set all values to false
# (Not recommended for production)"""
    
    def _patch_ebs_encryption(self, finding: Dict) -> str:
        """Generate patch for EBS encryption"""
        volume_id = finding['evidence'].get('volume_id')
        
        return f"""# Enable EBS encryption
# Volume: {volume_id}

# Note: Cannot encrypt existing volume in-place
# Must create snapshot, copy with encryption, create new volume

# Step 1: Create encrypted snapshot
resource "aws_ebs_snapshot" "{volume_id}_encrypted" {{
  volume_id = aws_ebs_volume.{volume_id}.id
  description = "Encrypted snapshot"
}}

# Step 2: Create new encrypted volume from snapshot
resource "aws_ebs_volume" "{volume_id}_encrypted" {{
  availability_zone = aws_ebs_volume.{volume_id}.availability_zone
  snapshot_id       = aws_ebs_snapshot.{volume_id}_encrypted.id
+ encrypted         = true
  size              = aws_ebs_volume.{volume_id}.size
}}

# Step 3: Detach old volume, attach new volume
# Step 4: Delete old volume after verification

# Rollback: Reattach original volume"""
