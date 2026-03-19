# Change Impact Simulation - Feature Documentation

## Overview

The Change Impact Simulator is an advanced feature that predicts the operational impact of applying remediation fixes. It provides enterprise-grade change management guidance including risk assessment, downtime prediction, blast radius analysis, safety checklists, and rollback procedures.

## Features

### 1. Change Type Classification

Every finding is automatically classified into a change category:

- **REQUIRES_INSTANCE_RESTART** - EC2 instance must be stopped and restarted
- **DESTRUCTIVE_CHANGE** - Resource will be permanently deleted
- **NETWORK_POLICY_CHANGE** - Security group or network rules modified
- **ACCESS_CONTROL_CHANGE** - S3 bucket or resource access permissions changed
- **PERMISSION_CHANGE** - IAM policies or roles modified
- **NETWORK_RESOURCE_DELETION** - Elastic IP or network resource removed
- **REQUIRES_VOLUME_REPLACEMENT** - EBS volume must be replaced (e.g., for encryption)

### 2. Risk Level Assessment

Automated risk classification based on change type:

**Low Risk:**
- Access control changes (S3 bucket policies)
- Network resource deletion (unused Elastic IPs)
- Enabling encryption or logging
- Tagging changes

**Medium Risk:**
- EC2 instance resizing
- Security group rule tightening
- IAM policy modifications
- Network policy changes

**High Risk:**
- Resource deletion
- IAM permission restrictions
- Infrastructure replacement
- Volume encryption (requires replacement)

### 3. Downtime Prediction

Deterministic downtime estimation:

| Change Type | Probability | Estimated Time | Details |
|------------|-------------|----------------|---------|
| Instance Restart | Possible | 1-2 minutes | Instance must be stopped and restarted |
| Network Policy | Possible | 0-30 seconds | Brief connection interruption |
| Access Control | None | 0 | Immediate, non-disruptive |
| Destructive | None | 0 | Resource not in use |
| Permission Change | Possible | 0 | May cause auth failures |
| Volume Replacement | Guaranteed | 5-15 minutes | Detach, replace, reattach |

### 4. Blast Radius Analysis

Uses the dependency graph to identify:
- **Affected Services** - Direct services impacted by the change
- **Blast Radius** - All connected resources that may be affected
- **Service Mapping** - Human-readable service names

Example:
```
EC2 Instance Change:
  Affected Services:
    • EC2 Instance (i-1234567890abcdef0)
    • Security Group (sg-0123456789abcdef0)
    • EBS Volume (vol-0123456789abcdef0)
  
  Blast Radius: 5 connected resources
```

### 5. Safety Checklist

Automated generation of pre-change safety checks:

**For Instance Restart:**
- ✓ Verify instance is not a single point of failure
- ✓ Check if instance is part of an Auto Scaling group
- ✓ Confirm load balancer health checks are configured
- ✓ Verify backup instances are available
- ✓ Schedule change during maintenance window
- ✓ Notify dependent teams
- ✓ Test application startup
- ✓ Monitor CloudWatch metrics post-change

**For Network Policy Change:**
- ✓ Document current security group rules
- ✓ Verify required application ports
- ✓ Confirm internal service communication paths
- ✓ Check automation dependencies
- ✓ Test connectivity from allowed sources
- ✓ Ensure monitoring/logging access maintained
- ✓ Have rollback plan ready
- ✓ Notify security team

**For Destructive Change:**
- ✓ Create snapshot or backup before deletion
- ✓ Verify resource is truly unused
- ✓ Confirm no automation references
- ✓ Check tags for importance indicators
- ✓ Review resource history
- ✓ Obtain approval from owner
- ✓ Document deletion
- ✓ Set snapshot retention policy

### 6. Rollback Procedures

Automatic generation of rollback instructions:

**Example - EC2 Resize Rollback:**
```bash
# Option 1 - Terraform
1. Revert instance_type to 'm5.4xlarge' in .tf file
2. Run: terraform plan
3. Run: terraform apply

# Option 2 - AWS CLI
1. Stop instance: aws ec2 stop-instances --instance-ids i-xxx
2. Wait: aws ec2 wait instance-stopped --instance-ids i-xxx
3. Modify: aws ec2 modify-instance-attribute --instance-id i-xxx --instance-type m5.4xlarge
4. Start: aws ec2 start-instances --instance-ids i-xxx

# Verification
aws ec2 describe-instances --instance-ids i-xxx --query 'Reservations[0].Instances[0].InstanceType'
```

### 7. Recommendations

Context-aware recommendations based on risk and change type:

- ⚠️ HIGH RISK: Test in non-production first
- 📋 Create detailed rollback plan
- 👥 Obtain approval from team lead
- ⚡ Schedule during maintenance window
- 📊 Monitor metrics closely
- 🔄 Plan for service interruption
- 💾 Create backup/snapshot
- 🔒 Test connectivity after change
- 💰 Potential savings highlighted
- 🔴 Security issue prioritization

### 8. Complexity Scoring

Automated complexity score (0-100) based on:
- Risk level (40 points for high, 20 for medium, 5 for low)
- Downtime probability (30 for guaranteed, 15 for possible)
- Blast radius size (2 points per connected resource, max 20)
- Affected services count (3 points per service, max 10)

**Complexity Levels:**
- 0-29: Simple change
- 30-59: Moderate change
- 60-100: Complex change

## Usage

### In the UI

1. Navigate to "📊 Findings" page
2. Select a finding from the table
3. Click on the "⚡ Change Impact Simulation" tab
4. Review the impact assessment

### Programmatically

```python
from impact.impact_simulator import ImpactSimulator
from graph.dependency_graph import DependencyGraph

# Initialize simulator
simulator = ImpactSimulator()

# Simulate impact
impact = simulator.simulate_change(finding, dependency_graph)

# Access results
print(f"Risk Level: {impact['risk_level']}")
print(f"Downtime: {impact['estimated_downtime']}")
print(f"Affected Services: {impact['affected_services']}")
print(f"Safety Checks: {impact['safety_checks']}")
print(f"Rollback Steps: {impact['rollback_steps']}")

# Get complexity score
complexity = simulator.get_change_complexity_score(impact)
print(f"Complexity: {complexity}/100")
```

## Integration with Priority Scoring

The impact simulator integrates with the priority scoring system:

**Original Formula:**
```
priority_score = (cost_savings × weight) + (severity × weight) - (change_risk × weight)
```

**Enhanced Formula:**
```
priority_score = (cost_savings × weight) + (severity × weight) - (change_risk × weight)

If impact_risk_level == "High":
    priority_score -= additional_penalty (20 points)
```

This ensures high-risk changes are deprioritized unless they have significant cost savings or critical security impact.

## UI Components

### Risk Level Display
Color-coded risk indicators:
- 🟢 Low Risk (Green)
- 🟡 Medium Risk (Orange)
- 🔴 High Risk (Red)

### Metrics Cards
- Risk Level
- Downtime Probability
- Estimated Downtime

### Affected Services List
Human-readable service names with resource IDs

### Blast Radius Warning
Alert when multiple resources are affected

### Recommendations Section
Prioritized list of actions to take

### Safety Checklist
Interactive checklist of pre-change verifications

### Rollback Plan
Code block with step-by-step rollback instructions

### Complexity Progress Bar
Visual indicator of change complexity

## Example Output

```
⚡ Change Impact Simulation

Risk Level: 🟡 Medium
Downtime Probability: Possible
Estimated Downtime: 1-2 minutes

Change Type: REQUIRES_INSTANCE_RESTART
Instance must be stopped and restarted

🎯 Affected Services
• EC2 Instance (i-1234567890abcdef0)
• Security Group (sg-0123456789abcdef0)
• EBS Volume (vol-0123456789abcdef0)

⚠️ This change may affect 5 connected resources

💡 Recommendations
⚡ MEDIUM RISK: Schedule during maintenance window if possible
📊 Monitor metrics closely after applying change
🔄 Plan for brief service interruption during restart
✅ Verify redundancy before proceeding
💰 Potential savings: $560.64/month ($6,727.68/year)

✅ Safety Checklist
✓ Verify instance is not a single point of failure
✓ Check if instance is part of an Auto Scaling group
✓ Confirm load balancer health checks are configured
✓ Verify backup instances are available
✓ Schedule change during maintenance window
✓ Notify dependent teams of planned downtime
✓ Test application startup after restart
✓ Monitor CloudWatch metrics post-change

🔄 Rollback Plan
[Detailed rollback instructions...]

📊 Change Complexity Score
45/100 - Moderate change
```

## Benefits

1. **Risk Mitigation** - Understand potential impact before making changes
2. **Downtime Planning** - Predict and plan for service interruptions
3. **Safety Assurance** - Comprehensive pre-change checklists
4. **Quick Recovery** - Ready-to-use rollback procedures
5. **Informed Decisions** - Data-driven change management
6. **Compliance** - Document change procedures for audits
7. **Team Communication** - Clear guidance for all stakeholders

## Best Practices

1. **Always Review Impact** - Check simulation before applying any fix
2. **Follow Safety Checks** - Complete all checklist items
3. **Test in Non-Prod** - For high-risk changes, test first
4. **Schedule Appropriately** - Use maintenance windows for medium/high risk
5. **Prepare Rollback** - Have rollback plan ready before starting
6. **Monitor Post-Change** - Watch metrics after applying fixes
7. **Document Changes** - Keep records of what was changed and why

## Technical Details

### Architecture

```
Finding → Impact Simulator → Risk Rules → Impact Assessment
                ↓
         Dependency Graph → Blast Radius Analysis
                ↓
         Output: Complete Impact Report
```

### Files

- `impact/impact_simulator.py` - Main simulator logic
- `impact/risk_rules.py` - Risk classification rules
- `dashboard/detail_view.py` - UI integration
- `scoring/priority_scoring.py` - Priority adjustment

### Extensibility

To add new change types:

1. Add to `CHANGE_TYPES` in `risk_rules.py`
2. Define risk level in `RISK_LEVELS`
3. Add downtime rules in `DOWNTIME_RULES`
4. Implement safety checks in `get_safety_checks()`
5. Add rollback steps in `get_rollback_steps()`

## Testing

Run the impact simulator test:

```bash
python test_impact_simulator.py
```

This will:
- Load sample data
- Run detection rules
- Simulate impact for all findings
- Display results and statistics

## Future Enhancements

- Machine learning for downtime prediction
- Historical change success rates
- Team-specific safety checklists
- Integration with change management systems
- Automated rollback execution
- Real-time impact monitoring
- Change approval workflows

## Summary

The Change Impact Simulator transforms StratusIQ from a detection tool into a complete change management platform. It provides the operational guidance needed to safely apply infrastructure changes in production environments.
