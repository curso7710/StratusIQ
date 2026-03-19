"""Terraform plan JSON parser"""
import json
from typing import Dict, List
from utils.logging_utils import setup_logger

logger = setup_logger(__name__)


class TerraformParser:
    """Parse Terraform plan JSON and normalize resources"""
    
    def __init__(self):
        self.resources = []
    
    def parse_plan(self, plan_data: Dict) -> List[Dict]:
        """Parse Terraform plan JSON"""
        self.resources = []
        
        # Handle both planned_values and configuration formats
        if "planned_values" in plan_data:
            root_module = plan_data["planned_values"].get("root_module", {})
            self._parse_module(root_module)
        elif "configuration" in plan_data:
            root_module = plan_data["configuration"].get("root_module", {})
            self._parse_configuration(root_module)
        
        logger.info(f"Parsed {len(self.resources)} resources from Terraform plan")
        return self.resources
    
    def _parse_module(self, module: Dict):
        """Parse module resources"""
        resources = module.get("resources", [])
        
        for resource in resources:
            normalized = self._normalize_resource(resource)
            if normalized:
                self.resources.append(normalized)
        
        # Parse child modules
        for child_module in module.get("child_modules", []):
            self._parse_module(child_module)
    
    def _parse_configuration(self, module: Dict):
        """Parse configuration format"""
        resources = module.get("resources", [])
        
        for resource in resources:
            normalized = self._normalize_config_resource(resource)
            if normalized:
                self.resources.append(normalized)
    
    def _normalize_resource(self, resource: Dict) -> Dict:
        """Normalize resource to standard schema"""
        resource_type = resource.get("type", "")
        address = resource.get("address", "")
        values = resource.get("values", {})
        
        normalized = {
            "resource_id": address,
            "type": resource_type,
            "config": values,
            "relationships": self._extract_relationships(resource_type, values),
            "metrics": {}
        }
        
        return normalized
    
    def _normalize_config_resource(self, resource: Dict) -> Dict:
        """Normalize configuration resource"""
        resource_type = resource.get("type", "")
        name = resource.get("name", "")
        expressions = resource.get("expressions", {})
        
        # Convert expressions to values
        config = {}
        for key, expr in expressions.items():
            if isinstance(expr, dict) and "constant_value" in expr:
                config[key] = expr["constant_value"]
            elif isinstance(expr, dict) and "references" in expr:
                config[key] = expr["references"]
        
        normalized = {
            "resource_id": f"{resource_type}.{name}",
            "type": resource_type,
            "config": config,
            "relationships": [],
            "metrics": {}
        }
        
        return normalized
    
    def _extract_relationships(self, resource_type: str, values: Dict) -> List[str]:
        """Extract resource relationships"""
        relationships = []
        
        if resource_type == "aws_instance":
            if "vpc_security_group_ids" in values:
                relationships.extend(values["vpc_security_group_ids"])
            if "subnet_id" in values:
                relationships.append(values["subnet_id"])
        
        elif resource_type == "aws_ebs_volume":
            if "availability_zone" in values:
                relationships.append(values["availability_zone"])
        
        elif resource_type == "aws_s3_bucket":
            if "bucket" in values:
                relationships.append(f"s3://{values['bucket']}")
        
        return relationships
    
    def parse_file(self, filepath: str) -> List[Dict]:
        """Parse Terraform plan from file"""
        with open(filepath, 'r') as f:
            plan_data = json.load(f)
        return self.parse_plan(plan_data)
