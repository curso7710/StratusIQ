# StratusIQ Quick Start

## 5-Minute Setup

### 1. Install (30 seconds)
```bash
cd stratusiq
pip install -r requirements.txt
```

### 2. Test (30 seconds)
```bash
python test_installation.py
```

### 3. Run (10 seconds)
```bash
streamlit run app.py
```

### 4. Demo (3 minutes)
1. Go to "🔍 Scan" page
2. Select "Terraform Plan JSON"
3. Upload `examples/terraform_sample_plan.json`
4. Click "Analyze Infrastructure"
5. Explore findings!

## Expected Results

You should see:
- ✅ 6+ findings detected
- 💰 $500+ monthly savings potential
- 🔒 Multiple security issues
- 📊 Interactive dependency graph

## What You'll Find

### Cost Issues
- Overprovisioned m5.4xlarge instance
- Unattached 50GB EBS volume
- Unused resources

### Security Issues
- SSH port (22) open to internet
- Unencrypted EBS volumes
- Public S3 bucket
- IAM role with wildcard principal

## Next Steps

### Try AWS Scanning
1. Configure AWS credentials:
   ```bash
   aws configure
   ```
2. Select "AWS Read-Only Scan"
3. Click "Scan AWS Infrastructure"

### Explore Features
- 📊 Filter findings by category/severity
- 🔧 View Terraform patches
- 💻 Copy AWS CLI commands
- 📖 Read detailed explanations
- 🔗 Visualize dependency graph
- 📄 Generate PDF report

## Common Commands

### Generate Terraform Plan
```bash
terraform plan -out=tfplan
terraform show -json tfplan > plan.json
```

### Configure AWS Credentials
```bash
aws configure
# OR
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
```

### Run with Auto-Reload
```bash
streamlit run app.py --server.runOnSave true
```

## Troubleshooting

### "Module not found"
```bash
pip install -r requirements.txt
```

### "AWS credentials not found"
```bash
aws configure
# OR use "Use default AWS credentials" checkbox
```

### "Streamlit won't start"
```bash
python -m streamlit run app.py
```

## Key Files

- `app.py` - Main application
- `config.py` - Settings and pricing
- `examples/terraform_sample_plan.json` - Demo data
- `examples/iam_readonly_policy.json` - AWS policy

## Documentation

- `README.md` - Overview and features
- `SETUP.md` - Detailed installation
- `USAGE_GUIDE.md` - How to use each feature
- `ARCHITECTURE.md` - Technical details

## Support

Questions? Check the docs or review the code!

---

**Ready to optimize your cloud infrastructure? Let's go! 🚀**
