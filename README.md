# StratusIQ - Cloud Cost & Security Intelligence Platform

A production-ready platform for analyzing cloud infrastructure configurations, detecting cost inefficiencies and security vulnerabilities, and generating remediation artifacts.

## Features

- **Multi-Source Input**: Analyze Terraform plans or scan live AWS infrastructure
- **Cost Optimization**: Detect idle resources, overprovisioned instances, and unused assets
- **Security Analysis**: Identify misconfigurations, open security groups, and compliance issues
- **Dependency Mapping**: Visualize resource relationships and blast radius
- **Priority Scoring**: Rank findings by impact, cost savings, and risk
- **Fix Generation**: Auto-generate Terraform patches and AWS CLI commands
- **Detailed Explanations**: Understand why issues were flagged and how to fix them
- **PDF Reports**: Generate comprehensive reports for stakeholders

## Quick Start

### Installation

```bash
cd stratusiq
pip install -r requirements.txt
```

### Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## Usage

### Option 1: Terraform Plan Analysis

1. Generate a Terraform plan in JSON format:
```bash
terraform plan -out=tfplan
terraform show -json tfplan > plan.json
```

2. Upload the `plan.json` file in the StratusIQ UI
3. Click "Analyze Infrastructure"

### Option 2: AWS Live Scan

1. Configure AWS credentials with read-only permissions (see IAM policy below)
2. Select "AWS Read-Only Scan" in the UI
3. Choose your region and click "Scan AWS Infrastructure"

## IAM Policy for AWS Scanning

Use the IAM policy in `examples/iam_readonly_policy.json` to create a read-only role:

```bash
aws iam create-policy \
  --policy-name StratusIQReadOnly \
  --policy-document file://examples/iam_readonly_policy.json
```

## Detection Rules

### Cost Optimization (6 rules)
1. Idle EC2 instances (CPU < 10%)
2. Overprovisioned EC2 (CPU < 30%)
3. Unattached EBS volumes
4. Unused Elastic IPs
5. Large instances with low utilization
6. Orphaned EBS snapshots

### Security (8 rules)
1. Security groups open to 0.0.0.0/0 on risky ports
2. Public S3 buckets
3. Missing S3 public access block
4. IAM policies with wildcard actions
5. IAM policies with wildcard resources
6. Unencrypted EBS volumes
7. CloudTrail disabled
8. Old IAM access keys

## Architecture

```
stratusiq/
├── app.py                      # Main Streamlit application
├── config.py                   # Configuration and pricing data
├── scanner/                    # Input parsers
│   ├── terraform_parser.py    # Terraform plan JSON parser
│   └── aws_scanner.py         # AWS API scanner
├── engine/                     # Detection rules
│   ├── rule_engine.py         # Rule orchestrator
│   ├── cost_rules.py          # Cost optimization rules
│   └── security_rules.py      # Security rules
├── graph/                      # Dependency analysis
│   └── dependency_graph.py    # NetworkX graph builder
├── scoring/                    # Priority calculation
│   └── priority_scoring.py    # Scoring algorithm
├── fixes/                      # Remediation generation
│   ├── terraform_patch_generator.py
│   └── cli_fix_generator.py
├── llm/                        # Explanation engine
│   └── explanation_engine.py  # Finding explanations
├── dashboard/                  # UI components
│   ├── findings_table.py      # Findings table
│   ├── detail_view.py         # Finding details
│   └── graph_view.py          # Dependency graph viz
├── report/                     # Report generation
│   └── report_generator.py    # PDF report builder
└── utils/                      # Utilities
    ├── helpers.py
    └── logging_utils.py
```

## Priority Scoring Algorithm

```
priority_score = (cost_savings_weight × estimated_savings)
                + (severity_weight × severity_score)
                - (change_risk_weight × risk_score)
```

Weights:
- Cost savings: 1.0
- Severity: 0.5
- Change risk: 0.3

## Security Design

- Read-only IAM permissions only
- No credential storage
- Sensitive fields redacted in logs
- Audit trail for all scans
- No auto-execution of fixes

## Example Workflow

1. **Scan**: Upload Terraform plan or scan AWS
2. **Review**: Browse findings table with filters
3. **Analyze**: View detailed evidence and impact
4. **Remediate**: Copy Terraform patches or CLI commands
5. **Report**: Generate PDF for stakeholders

## Testing with Sample Data

A sample Terraform plan is provided in `examples/terraform_sample_plan.json`:

```bash
# In the UI, upload examples/terraform_sample_plan.json
```

This will detect:
- Overprovisioned m5.4xlarge instance
- Security group open to 0.0.0.0/0 on port 22
- Unattached EBS volume
- Unencrypted EBS volumes
- Public S3 bucket
- IAM role with wildcard principal

## Requirements

- Python 3.8+
- Streamlit 1.31+
- boto3 (for AWS scanning)
- networkx (for dependency graphs)
- plotly (for visualizations)
- reportlab (for PDF reports)

## License

MIT License

## Support

For issues or questions, please open an issue on GitHub.
