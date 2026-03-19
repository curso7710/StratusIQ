# Change Impact Simulation - Quick Reference

## Change Types

| Change Type | Risk | Downtime | Example |
|------------|------|----------|---------|
| REQUIRES_INSTANCE_RESTART | Medium | 1-2 min | EC2 resize |
| DESTRUCTIVE_CHANGE | High | None | Delete volume |
| NETWORK_POLICY_CHANGE | Medium | 0-30 sec | Close SG port |
| ACCESS_CONTROL_CHANGE | Low | None | S3 private |
| PERMISSION_CHANGE | Medium | None | IAM restrict |
| NETWORK_RESOURCE_DELETION | Low | None | Release EIP |
| REQUIRES_VOLUME_REPLACEMENT | High | 5-15 min | Encrypt EBS |

## Risk Levels

### 🟢 Low Risk
- Access control changes
- Network resource deletion
- Enabling encryption/logging
- Tagging changes

### 🟡 Medium Risk
- EC2 resizing
- Security group tightening
- IAM policy modifications
- Network policy changes

### 🔴 High Risk
- Resource deletion
- IAM permission restrictions
- Infrastructure replacement
- Volume encryption

## Complexity Scoring

```
Score = Risk (0-40) + Downtime (0-30) + Blast Radius (0-20) + Services (0-10)
```

- **0-29:** Simple change
- **30-59:** Moderate change
- **60-100:** Complex change

## Safety Checklist Examples

### EC2 Restart
- ✓ Not single point of failure
- ✓ Auto Scaling group check
- ✓ Load balancer health checks
- ✓ Backup instances available
- ✓ Maintenance window scheduled
- ✓ Teams notified
- ✓ Test startup
- ✓ Monitor metrics

### Network Change
- ✓ Document current rules
- ✓ Verify app ports
- ✓ Confirm service paths
- ✓ Check automation deps
- ✓ Test connectivity
- ✓ Maintain monitoring access
- ✓ Rollback ready
- ✓ Notify security team

### Destructive Change
- ✓ Create snapshot/backup
- ✓ Verify truly unused
- ✓ Check automation refs
- ✓ Review tags
- ✓ Check history
- ✓ Owner approval
- ✓ Document deletion
- ✓ Retention policy

## Quick Rollback

### EC2 Resize
```bash
aws ec2 stop-instances --instance-ids i-xxx
aws ec2 wait instance-stopped --instance-ids i-xxx
aws ec2 modify-instance-attribute --instance-id i-xxx --instance-type original
aws ec2 start-instances --instance-ids i-xxx
```

### Security Group
```bash
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxx \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0
```

### S3 Access
```bash
aws s3api put-bucket-acl --bucket bucket-name --acl private
```

## Best Practices

1. **Always Review** - Check impact before applying
2. **Follow Checklist** - Complete all safety items
3. **Test First** - High-risk changes in non-prod
4. **Schedule Smart** - Use maintenance windows
5. **Prepare Rollback** - Have plan ready
6. **Monitor After** - Watch metrics post-change
7. **Document** - Record what and why

## UI Navigation

1. Go to "📊 Findings"
2. Select a finding
3. Click "⚡ Change Impact Simulation" tab
4. Review:
   - Risk level (color-coded)
   - Downtime estimate
   - Affected services
   - Safety checklist
   - Rollback plan
   - Complexity score

## Priority Adjustment

High-risk changes get -20 priority penalty:

```
Original: priority = cost + severity - risk
Enhanced: priority = cost + severity - risk - (20 if high_risk)
```

## Testing

```bash
python test_impact_simulator.py
```

Shows:
- Change types detected
- Risk levels assigned
- Downtime predictions
- Affected services
- Complexity scores
- Distribution statistics

## Integration

```python
from impact.impact_simulator import ImpactSimulator

simulator = ImpactSimulator()
impact = simulator.simulate_change(finding, graph)

print(impact['risk_level'])
print(impact['safety_checks'])
print(impact['rollback_steps'])
```

## Key Metrics

- **7 Change Types** classified
- **3 Risk Levels** (Low/Medium/High)
- **Downtime Estimates** for each type
- **Automated Checklists** per change type
- **Rollback Instructions** auto-generated
- **Complexity Score** 0-100 scale

## When to Use

- ✅ Before applying any fix
- ✅ Planning maintenance windows
- ✅ Assessing change risk
- ✅ Preparing rollback plans
- ✅ Communicating with teams
- ✅ Documenting changes
- ✅ Compliance audits

## Color Coding

- 🟢 **Green** - Low risk, safe to proceed
- 🟡 **Orange** - Medium risk, schedule carefully
- 🔴 **Red** - High risk, test in non-prod first

---

**Quick Tip:** Always check the Change Impact Simulation tab before applying any fix. It takes 5 seconds and could save hours of downtime.
