"""AWS infrastructure scanner using boto3"""
import boto3
from typing import Dict, List
from datetime import datetime, timedelta
from utils.logging_utils import setup_logger

logger = setup_logger(__name__)


class AWSScanner:
    """Scan AWS infrastructure using read-only credentials"""
    
    def __init__(self, region: str = "us-east-1"):
        self.region = region
        self.resources = []
    
    def scan_infrastructure(self, aws_access_key: str = None, 
                          aws_secret_key: str = None) -> List[Dict]:
        """Scan AWS infrastructure"""
        self.resources = []
        
        try:
            # Initialize boto3 clients
            if aws_access_key and aws_secret_key:
                session = boto3.Session(
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key,
                    region_name=self.region
                )
            else:
                session = boto3.Session(region_name=self.region)
            
            # Scan different resource types
            self._scan_ec2_instances(session)
            self._scan_security_groups(session)
            self._scan_ebs_volumes(session)
            self._scan_s3_buckets(session)
            self._scan_iam_roles(session)
            self._scan_elastic_ips(session)
            
            logger.info(f"Scanned {len(self.resources)} AWS resources")
            return self.resources
            
        except Exception as e:
            logger.error(f"Error scanning AWS: {str(e)}")
            raise
    
    def _scan_ec2_instances(self, session):
        """Scan EC2 instances"""
        try:
            ec2 = session.client('ec2')
            response = ec2.describe_instances()
            
            for reservation in response.get('Reservations', []):
                for instance in reservation.get('Instances', []):
                    # Get CPU metrics
                    cpu_avg = self._get_cpu_utilization(
                        session, instance['InstanceId']
                    )
                    
                    resource = {
                        "resource_id": instance['InstanceId'],
                        "type": "aws_instance",
                        "config": {
                            "instance_type": instance.get('InstanceType'),
                            "state": instance.get('State', {}).get('Name'),
                            "vpc_security_group_ids": [
                                sg['GroupId'] for sg in instance.get('SecurityGroups', [])
                            ],
                            "subnet_id": instance.get('SubnetId'),
                            "tags": instance.get('Tags', []),
                        },
                        "relationships": [
                            sg['GroupId'] for sg in instance.get('SecurityGroups', [])
                        ],
                        "metrics": {
                            "cpu_average": cpu_avg
                        }
                    }
                    self.resources.append(resource)
        except Exception as e:
            logger.warning(f"Could not scan EC2 instances: {str(e)}")
    
    def _scan_security_groups(self, session):
        """Scan security groups"""
        try:
            ec2 = session.client('ec2')
            response = ec2.describe_security_groups()
            
            for sg in response.get('SecurityGroups', []):
                resource = {
                    "resource_id": sg['GroupId'],
                    "type": "aws_security_group",
                    "config": {
                        "group_name": sg.get('GroupName'),
                        "description": sg.get('Description'),
                        "ingress": sg.get('IpPermissions', []),
                        "egress": sg.get('IpPermissionsEgress', []),
                        "vpc_id": sg.get('VpcId'),
                    },
                    "relationships": [],
                    "metrics": {}
                }
                self.resources.append(resource)
        except Exception as e:
            logger.warning(f"Could not scan security groups: {str(e)}")
    
    def _scan_ebs_volumes(self, session):
        """Scan EBS volumes"""
        try:
            ec2 = session.client('ec2')
            response = ec2.describe_volumes()
            
            for volume in response.get('Volumes', []):
                resource = {
                    "resource_id": volume['VolumeId'],
                    "type": "aws_ebs_volume",
                    "config": {
                        "size": volume.get('Size'),
                        "volume_type": volume.get('VolumeType'),
                        "state": volume.get('State'),
                        "encrypted": volume.get('Encrypted', False),
                        "attachments": volume.get('Attachments', []),
                    },
                    "relationships": [
                        att['InstanceId'] for att in volume.get('Attachments', [])
                    ],
                    "metrics": {}
                }
                self.resources.append(resource)
        except Exception as e:
            logger.warning(f"Could not scan EBS volumes: {str(e)}")
    
    def _scan_s3_buckets(self, session):
        """Scan S3 buckets"""
        try:
            s3 = session.client('s3')
            response = s3.list_buckets()
            
            for bucket in response.get('Buckets', []):
                bucket_name = bucket['Name']
                
                # Check public access block
                try:
                    public_block = s3.get_public_access_block(Bucket=bucket_name)
                    public_block_config = public_block.get('PublicAccessBlockConfiguration', {})
                except:
                    public_block_config = {}
                
                # Check bucket ACL
                try:
                    acl = s3.get_bucket_acl(Bucket=bucket_name)
                    grants = acl.get('Grants', [])
                except:
                    grants = []
                
                resource = {
                    "resource_id": bucket_name,
                    "type": "aws_s3_bucket",
                    "config": {
                        "bucket": bucket_name,
                        "public_access_block": public_block_config,
                        "acl_grants": grants,
                    },
                    "relationships": [],
                    "metrics": {}
                }
                self.resources.append(resource)
        except Exception as e:
            logger.warning(f"Could not scan S3 buckets: {str(e)}")
    
    def _scan_iam_roles(self, session):
        """Scan IAM roles"""
        try:
            iam = session.client('iam')
            response = iam.list_roles()
            
            for role in response.get('Roles', []):
                role_name = role['RoleName']
                
                # Get attached policies
                try:
                    policies_response = iam.list_attached_role_policies(RoleName=role_name)
                    policies = policies_response.get('AttachedPolicies', [])
                except:
                    policies = []
                
                resource = {
                    "resource_id": role['Arn'],
                    "type": "aws_iam_role",
                    "config": {
                        "role_name": role_name,
                        "arn": role['Arn'],
                        "assume_role_policy": role.get('AssumeRolePolicyDocument'),
                        "attached_policies": policies,
                    },
                    "relationships": [],
                    "metrics": {}
                }
                self.resources.append(resource)
        except Exception as e:
            logger.warning(f"Could not scan IAM roles: {str(e)}")
    
    def _scan_elastic_ips(self, session):
        """Scan Elastic IPs"""
        try:
            ec2 = session.client('ec2')
            response = ec2.describe_addresses()
            
            for address in response.get('Addresses', []):
                resource = {
                    "resource_id": address.get('AllocationId', address.get('PublicIp')),
                    "type": "aws_eip",
                    "config": {
                        "public_ip": address.get('PublicIp'),
                        "allocation_id": address.get('AllocationId'),
                        "association_id": address.get('AssociationId'),
                        "instance_id": address.get('InstanceId'),
                    },
                    "relationships": [],
                    "metrics": {}
                }
                self.resources.append(resource)
        except Exception as e:
            logger.warning(f"Could not scan Elastic IPs: {str(e)}")
    
    def _get_cpu_utilization(self, session, instance_id: str) -> float:
        """Get average CPU utilization for instance"""
        try:
            cloudwatch = session.client('cloudwatch')
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=7)
            
            response = cloudwatch.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Average']
            )
            
            datapoints = response.get('Datapoints', [])
            if datapoints:
                avg = sum(dp['Average'] for dp in datapoints) / len(datapoints)
                return round(avg, 2)
            return 0.0
        except:
            return 0.0
