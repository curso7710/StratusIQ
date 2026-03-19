# StratusIQ Usage Guide

## Overview

StratusIQ analyzes cloud infrastructure to identify cost optimization opportunities and security vulnerabilities, then generates actionable remediation artifacts.

## Workflow

```
1. Scan Infrastructure → 2. Review Findings → 3. Analyze Details → 4. Apply Fixes → 5. Generate Report
```

## Page-by-Page Guide

### 1. Scan Page (🔍 Scan)

#### Terraform Plan Analysis

**When to use:** You have Terraform-managed infrastructure and want to analyze planned changes before applying.

**Steps:**
1. Generate Terraform plan:
   ```bash
   terraform plan -out=tfplan
   terraform show -json tfplan > plan.json
   ```
2. Upload `plan.json` in the UI
3. Click "Analyze Infrastructure"

**What it detects:**
- Resource configurations from Terraform state
- Planned resource changes
- Configuration issues before deployment

#### AWS Live Scan

**When to use:** You want to analyze your current AWS infrastructure state.

**Steps:**
1. Configure AWS credentials (see Setup Guide)
2. Select your AWS region
3. Choose credential method:
   - Default credentials (from AWS CLI)
   - Manual entry (access key + secret)
4. Click "Scan AWS Infrastructure"

**What it scans:**
- EC2 instances (with CPU metrics)
- Security groups
- EBS volumes
- S3 buckets
- IAM roles
- Elastic IPs

**Scan time:** 30-120 seconds depending on resource count

### 2. Findings Page (📊 Findings)

#### Findings Table

**Filters available:**
- **Category:** Cost, Security
- **Severity:** Critical, High, Medium, Low
- **Min Savings:** Filter by minimum monthly savings

**Columns:**
- **Priority Score:** Higher = more important
- **Title:** Brief description
- **Category:** Cost or Security
- **Severity:** Risk level
- **Monthly Savings:** Estimated cost reduction
- **Risk:** Change implementation risk
- **Confidence:** Detection confidence level

**Sorting:** Findings are pre-sorted by priority score (highest first)

#### Finding Details

Select a finding to view:

**Evidence Tab:**
- Raw data that triggered the detection
- Metrics and thresholds
- Resource configuration details

**Terraform Patch Tab:**
- Ready-to-apply Terraform code changes
- Before/after comparison
- Rollback instructions

**CLI Commands Tab:**
- AWS CLI commands for remediation
- Step-by-step execution guide
- Verification commands

**Explanation Tab:**
- Why the issue was flagged
- Security or cost impact
- What the fix does
- Trade-offs and considerations

**Impact Tab:**
- Affected resources
- Blast radius (connected resources)
- Change impact assessment

### 3. Dependency Graph Page (🔗 Dependency Graph)

**Purpose:** Visualize resource relationships and understand blast radius.

**Features:**
- Interactive graph visualization
- Color-coded by resource type
- Hover for resource details
- Graph statistics

**Use cases:**
- Understand resource dependencies before changes
- Identify tightly coupled resources
- Plan migration strategies
- Assess change impact

**Resource types shown:**
- 🟠 EC2 Instances
- 🔴 Security Groups
- 🔵 EBS Volumes
- 🟢 S3 Buckets
- 🟣 IAM Roles
- 🟡 Elastic IPs

### 4. Report Page (📄 Report)

**Purpose:** Generate PDF reports for stakeholders.

**Report contents:**
- Executive summary
- Total findings count
- Cost savings potential
- Top priority findings
- Detailed finding descriptions

**Steps:**
1. Enter report filename
2. Click "Generate PDF Report"
3. Download the generated PDF

**Use cases:**
- Share findings with management
- Document compliance issues
- Track remediation progress
- Quarterly cost reviews

## Common Workflows

### Workflow 1: Cost Optimization Review

1. **Scan** your AWS infrastructure
2. **Filter** findings by Category = "Cost"
3. **Sort** by Monthly Savings (descending)
4. **Review** top 5 findings
5. **Copy** Terraform patches or CLI commands
6. **Test** in non-production environment
7. **Apply** fixes to production
8. **Generate** report showing savings

### Workflow 2: Security Audit

1. **Scan** infrastructure
2. **Filter** by Category = "Security", Severity = "Critical" or "High"
3. **Review** each finding's evidence
4. **Check** blast radius in dependency graph
5. **Plan** remediation order (lowest risk first)
6. **Apply** security fixes
7. **Re-scan** to verify fixes
8. **Generate** compliance report

### Workflow 3: Pre-Deployment Check

1. **Generate** Terraform plan
2. **Upload** plan JSON to StratusIQ
3. **Review** findings for planned resources
4. **Fix** issues in Terraform code
5. **Re-plan** and re-analyze
6. **Deploy** when no critical issues remain

### Workflow 4: Quarterly Review

1. **Scan** all environments (dev, staging, prod)
2. **Compare** findings across environments
3. **Identify** patterns and recurring issues
4. **Generate** reports for each environment
5. **Present** to stakeholders
6. **Track** remediation progress

## Understanding Findings

### Cost Findings

**Idle EC2 Instance**
- **Trigger:** CPU < 10% for 7 days
- **Action:** Stop or terminate
- **Risk:** Low (can restart if needed)

**Overprovisioned EC2**
- **Trigger:** CPU < 30% for 7 days
- **Action:** Downsize instance type
- **Risk:** Medium (requires restart)

**Unattached EBS Volume**
- **Trigger:** Volume not attached to any instance
- **Action:** Delete after snapshot
- **Risk:** Low (data preserved in snapshot)

**Unused Elastic IP**
- **Trigger:** EIP not associated with instance
- **Action:** Release the IP
- **Risk:** Low (can allocate new IP)

### Security Findings

**Open Security Group**
- **Trigger:** Ingress rule with 0.0.0.0/0 on risky port
- **Action:** Restrict to specific CIDR
- **Risk:** Medium (may affect access)

**Public S3 Bucket**
- **Trigger:** Bucket ACL allows public read
- **Action:** Change ACL to private
- **Risk:** High (may break integrations)

**Missing S3 Public Access Block**
- **Trigger:** Public access block not enabled
- **Action:** Enable all four settings
- **Risk:** Low (defense in depth)

**Unencrypted EBS Volume**
- **Trigger:** Encryption not enabled
- **Action:** Create encrypted copy
- **Risk:** High (requires volume replacement)

## Best Practices

### Before Applying Fixes

1. **Review evidence** carefully
2. **Check blast radius** for dependencies
3. **Test in non-production** first
4. **Backup data** if applicable
5. **Plan rollback** strategy
6. **Schedule maintenance window** for high-risk changes

### Priority Order

1. **Critical security issues** (open ports, public buckets)
2. **High-cost optimizations** (large idle instances)
3. **Medium security issues** (missing encryption)
4. **Low-cost optimizations** (small unused resources)

### Validation

After applying fixes:
1. **Re-scan** infrastructure
2. **Verify** finding is resolved
3. **Test** application functionality
4. **Monitor** for 24-48 hours
5. **Document** changes made

## Tips and Tricks

### Filtering

- Use multiple filters to narrow results
- Start with Critical + High severity
- Filter by savings > $50/month for quick wins

### Batch Processing

- Group similar findings (e.g., all unattached volumes)
- Apply fixes in batches
- Use CLI commands for automation

### Automation

- Export findings to JSON
- Integrate with CI/CD pipelines
- Schedule regular scans
- Track findings over time

### Reporting

- Generate reports before and after remediation
- Show cost savings achieved
- Track security posture improvements
- Share with stakeholders quarterly

## Troubleshooting

### No Findings Detected

- Verify resources were scanned successfully
- Check if resources match detection criteria
- Review scan logs for errors

### Incorrect Savings Estimates

- Pricing is based on us-east-1 rates
- Actual savings may vary by region
- Reserved instances not accounted for

### False Positives

- Review evidence carefully
- Consider business context
- Adjust thresholds if needed
- Document exceptions

## Advanced Usage

### Custom Thresholds

Edit `config.py` to adjust:
- CPU thresholds
- Risky ports list
- Pricing data
- Scoring weights

### Integration

- Export findings as JSON
- Import into ticketing systems
- Automate with scripts
- Build custom dashboards

## Support

For questions or issues:
- Review this guide
- Check SETUP.md
- Review code documentation
- Open GitHub issue
