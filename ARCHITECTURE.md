# StratusIQ Architecture Documentation

## System Overview

StratusIQ is a cloud infrastructure analysis platform that converts infrastructure configurations into actionable insights with remediation artifacts.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         INPUT LAYER                              │
├─────────────────────────────────────────────────────────────────┤
│  Terraform Plan JSON          │         AWS Live Scan           │
│  (terraform_parser.py)        │      (aws_scanner.py)           │
└────────────────┬──────────────┴──────────────┬──────────────────┘
                 │                              │
                 └──────────────┬───────────────┘
                                │
                    ┌───────────▼───────────┐
                    │  Resource Normalizer  │
                    │  (Standard Schema)    │
                    └───────────┬───────────┘
                                │
                 ┌──────────────┴──────────────┐
                 │                             │
     ┌───────────▼──────────┐      ┌──────────▼─────────┐
     │  Dependency Graph    │      │   Detection Engine │
     │  (networkx)          │      │   (rule_engine.py) │
     │  - Build graph       │      │   - Cost rules     │
     │  - Blast radius      │      │   - Security rules │
     └───────────┬──────────┘      └──────────┬─────────┘
                 │                             │
                 └──────────────┬──────────────┘
                                │
                    ┌───────────▼───────────┐
                    │   Priority Scoring    │
                    │   (scoring algorithm) │
                    └───────────┬───────────┘
                                │
                 ┌──────────────┴──────────────┐
                 │                             │
     ┌───────────▼──────────┐      ┌──────────▼─────────┐
     │  Fix Generation      │      │  Explanation Engine│
     │  - Terraform patches │      │  - Why flagged     │
     │  - CLI commands      │      │  - Impact analysis │
     └───────────┬──────────┘      └──────────┬─────────┘
                 │                             │
                 └──────────────┬──────────────┘
                                │
                    ┌───────────▼───────────┐
                    │   OUTPUT LAYER        │
                    │   - Dashboard (UI)    │
                    │   - PDF Reports       │
                    └───────────────────────┘
```

## Component Details

### 1. Input Layer

#### Terraform Parser (`scanner/terraform_parser.py`)
- **Purpose:** Parse Terraform plan JSON files
- **Input:** Terraform plan output (`terraform show -json`)
- **Output:** Normalized resource list
- **Key Functions:**
  - `parse_plan()`: Main parsing entry point
  - `_normalize_resource()`: Convert to standard schema
  - `_extract_relationships()`: Build resource connections

#### AWS Scanner (`scanner/aws_scanner.py`)
- **Purpose:** Scan live AWS infrastructure
- **Input:** AWS credentials and region
- **Output:** Normalized resource list
- **Key Functions:**
  - `scan_infrastructure()`: Orchestrate all scans
  - `_scan_ec2_instances()`: Get EC2 data + metrics
  - `_scan_security_groups()`: Get SG rules
  - `_scan_ebs_volumes()`: Get volume data
  - `_scan_s3_buckets()`: Get bucket configs
  - `_scan_iam_roles()`: Get IAM policies
  - `_get_cpu_utilization()`: CloudWatch metrics

**Resource Schema:**
```python
{
    "resource_id": str,      # Unique identifier
    "type": str,             # aws_instance, aws_s3_bucket, etc.
    "config": dict,          # Resource configuration
    "relationships": list,   # Connected resource IDs
    "metrics": dict          # Performance metrics
}
```

### 2. Graph Layer

#### Dependency Graph (`graph/dependency_graph.py`)
- **Purpose:** Build and analyze resource relationships
- **Technology:** NetworkX directed graph
- **Key Functions:**
  - `build_graph()`: Create graph from resources
  - `get_blast_radius()`: Find affected resources
  - `get_connected_resources()`: Direct connections
  - `get_graph_data()`: Export for visualization

**Graph Structure:**
- Nodes: Resources
- Edges: Dependencies (EC2 → SG, EC2 → EBS, etc.)
- Algorithms: Descendants, ancestors, connected components

### 3. Detection Engine

#### Rule Engine (`engine/rule_engine.py`)
- **Purpose:** Orchestrate all detection rules
- **Key Functions:**
  - `run_all_checks()`: Execute all rules
  - `_enrich_with_blast_radius()`: Add impact data

#### Cost Rules (`engine/cost_rules.py`)
- **Rules Implemented:**
  1. Idle EC2 instances (CPU < 10%)
  2. Overprovisioned EC2 (CPU < 30%)
  3. Unattached EBS volumes
  4. Unused Elastic IPs
  5. Large instances with low utilization
  6. Orphaned snapshots (placeholder)

#### Security Rules (`engine/security_rules.py`)
- **Rules Implemented:**
  1. Open security groups (0.0.0.0/0 on risky ports)
  2. Public S3 buckets
  3. Missing S3 public access block
  4. IAM wildcard actions
  5. IAM wildcard resources
  6. Unencrypted EBS volumes
  7. CloudTrail disabled (placeholder)
  8. Old IAM keys (placeholder)

**Finding Schema:**
```python
{
    "id": str,                          # Unique finding ID
    "title": str,                       # Human-readable title
    "category": "cost" | "security",    # Finding type
    "severity": str,                    # critical/high/medium/low
    "estimated_monthly_savings": float, # Cost impact
    "evidence": dict,                   # Detection data
    "affected_resources": list,         # Resource IDs
    "blast_radius": list,               # Connected resources
    "confidence": str,                  # Detection confidence
    "change_risk": str                  # Implementation risk
}
```

### 4. Scoring Layer

#### Priority Scorer (`scoring/priority_scoring.py`)
- **Purpose:** Rank findings by priority
- **Algorithm:**
  ```
  priority_score = (cost_weight × savings)
                 + (severity_weight × severity_score)
                 - (risk_weight × risk_score)
  ```
- **Weights (configurable in `config.py`):**
  - Cost savings: 1.0
  - Severity: 0.5
  - Change risk: 0.3

- **Key Functions:**
  - `score_findings()`: Calculate and sort
  - `get_summary_stats()`: Aggregate metrics

### 5. Fix Generation Layer

#### Terraform Patch Generator (`fixes/terraform_patch_generator.py`)
- **Purpose:** Generate Terraform code patches
- **Output Format:** HCL with before/after comparison
- **Key Functions:**
  - `generate_patch()`: Route to specific generator
  - `_patch_*()`: Finding-specific patches

#### CLI Fix Generator (`fixes/cli_fix_generator.py`)
- **Purpose:** Generate AWS CLI commands
- **Output Format:** Bash scripts with comments
- **Key Functions:**
  - `generate_cli_command()`: Route to specific generator
  - `_cli_*()`: Finding-specific commands

**Features:**
- Step-by-step instructions
- Verification commands
- Rollback procedures
- Safety warnings

### 6. Explanation Layer

#### Explanation Engine (`llm/explanation_engine.py`)
- **Purpose:** Generate human-readable explanations
- **Approach:** Rule-based (can be replaced with LLM)
- **Output Sections:**
  - Why flagged
  - Cost/security impact
  - What the fix does
  - Trade-offs

**Design Philosophy:**
- Uses only structured finding data
- No guessing or hallucination
- Factual and actionable
- Context-aware explanations

### 7. Presentation Layer

#### Streamlit Dashboard (`app.py`)
- **Pages:**
  1. Scan: Input configuration
  2. Findings: Table with filters
  3. Dependency Graph: Visualization
  4. Report: PDF generation

#### Dashboard Components

**Findings Table** (`dashboard/findings_table.py`)
- Filterable data table
- Multi-select filters
- Finding selection

**Detail View** (`dashboard/detail_view.py`)
- Tabbed interface
- Evidence display
- Terraform patches
- CLI commands
- Explanations
- Impact analysis

**Graph View** (`dashboard/graph_view.py`)
- Interactive Plotly visualization
- Color-coded by resource type
- Hover tooltips
- Graph statistics

#### Report Generator (`report/report_generator.py`)
- **Technology:** ReportLab
- **Output:** PDF
- **Sections:**
  - Executive summary
  - Statistics table
  - Top findings
  - Detailed descriptions

## Data Flow

### Terraform Analysis Flow
```
1. User uploads plan.json
2. TerraformParser.parse_plan()
3. Resources normalized to standard schema
4. DependencyGraph.build_graph()
5. RuleEngine.run_all_checks()
6. PriorityScorer.score_findings()
7. Display in dashboard
```

### AWS Scan Flow
```
1. User provides credentials
2. AWSScanner.scan_infrastructure()
   - EC2: describe_instances + CloudWatch metrics
   - SG: describe_security_groups
   - EBS: describe_volumes
   - S3: list_buckets + get_bucket_acl
   - IAM: list_roles + list_attached_policies
3. Resources normalized to standard schema
4. [Same as steps 4-7 above]
```

### Finding Generation Flow
```
1. RuleEngine receives resources
2. For each rule:
   - Check conditions
   - Extract evidence
   - Calculate savings/severity
   - Create finding object
3. DependencyGraph enriches with blast radius
4. PriorityScorer calculates priority
5. Findings sorted by priority
```

## Configuration

### `config.py`
- EC2 pricing table
- EBS/EIP pricing
- Severity scores
- Scoring weights
- CPU thresholds
- Risky ports list

**Customization:**
- Adjust thresholds for your environment
- Update pricing for your region
- Modify scoring weights
- Add custom risky ports

## Security Design

### Read-Only Principle
- IAM policy grants only read permissions
- No write/modify/delete actions
- No credential storage
- Credentials used only for API calls

### Data Handling
- No PII storage
- Sensitive fields redacted in logs
- Audit trail for scans
- Local processing only

### Fix Safety
- No auto-execution
- Manual review required
- Rollback instructions provided
- Test in non-prod first

## Extensibility

### Adding New Rules

1. Create rule method in `cost_rules.py` or `security_rules.py`:
```python
def check_new_rule(self, resources: List[Dict]) -> List[Dict]:
    findings = []
    for resource in resources:
        # Check conditions
        if condition_met:
            finding = {
                "id": f"category-type-{resource['resource_id']}",
                "title": "Finding Title",
                # ... other fields
            }
            findings.append(finding)
    return findings
```

2. Register in `rule_engine.py`:
```python
all_findings.extend(self.cost_rules.check_new_rule(resources))
```

3. Add fix generators in `terraform_patch_generator.py` and `cli_fix_generator.py`

4. Add explanation in `explanation_engine.py`

### Adding New Resource Types

1. Update parser to extract new resource type
2. Add to dependency graph relationships
3. Create detection rules
4. Add to graph visualization colors

### Adding New Input Sources

1. Create new scanner in `scanner/`
2. Implement resource normalization
3. Add UI option in `app.py`
4. Update documentation

## Performance Considerations

### Scalability
- **Resources:** Tested up to 1000 resources
- **Findings:** Handles 100+ findings efficiently
- **Graph:** NetworkX scales to 10,000+ nodes

### Optimization Opportunities
- Cache CloudWatch metrics
- Parallel AWS API calls
- Incremental graph updates
- Finding deduplication

## Testing Strategy

### Unit Tests (Recommended)
- Test each rule independently
- Mock AWS responses
- Validate finding schema
- Test scoring algorithm

### Integration Tests
- End-to-end with sample data
- Test all input modes
- Verify fix generation
- Check report generation

### Manual Testing
- Use `test_installation.py`
- Test with `terraform_sample_plan.json`
- Verify UI functionality
- Test AWS scanning (if credentials available)

## Deployment Options

### Local Development
```bash
streamlit run app.py
```

### Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

### Streamlit Cloud
- Push to GitHub
- Deploy via share.streamlit.io
- Configure secrets for AWS

### Enterprise Deployment
- Run behind corporate proxy
- Integrate with SSO
- Store findings in database
- Schedule automated scans

## Future Enhancements

### Potential Features
- Multi-cloud support (Azure, GCP)
- Historical trending
- Automated fix application
- Slack/email notifications
- Custom rule builder UI
- API endpoint for CI/CD
- Database backend
- User authentication
- Team collaboration
- Finding assignment/tracking

### LLM Integration
- Replace rule-based explanations
- Natural language queries
- Automated fix validation
- Context-aware recommendations

## Troubleshooting

### Common Issues

**Import Errors:**
- Ensure running from `stratusiq/` directory
- Check Python path
- Verify all dependencies installed

**AWS Connection:**
- Verify credentials
- Check IAM permissions
- Confirm region availability

**No Findings:**
- Verify resources meet thresholds
- Check rule logic
- Review scan logs

**Graph Visualization:**
- Ensure networkx installed
- Check browser compatibility
- Verify graph data structure

## References

- Terraform JSON format: https://www.terraform.io/docs/internals/json-format.html
- AWS boto3 docs: https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
- NetworkX: https://networkx.org/documentation/stable/
- Streamlit: https://docs.streamlit.io/
