# StratusIQ Setup Guide

## Prerequisites

- Python 3.8 or higher
- pip package manager
- (Optional) AWS account with read-only credentials

## Installation Steps

### 1. Install Dependencies

```bash
cd stratusiq
pip install -r requirements.txt
```

### 2. Verify Installation

```bash
python -c "import streamlit; import boto3; import networkx; print('All dependencies installed successfully!')"
```

### 3. Run the Application

```bash
streamlit run app.py
```

The application will automatically open in your browser at `http://localhost:8501`

## Quick Test with Sample Data

1. Start the application
2. Navigate to "🔍 Scan" page
3. Select "Terraform Plan JSON"
4. Upload `examples/terraform_sample_plan.json`
5. Click "Analyze Infrastructure"

You should see:
- 6+ findings detected
- Cost savings opportunities
- Security vulnerabilities
- Dependency graph visualization

## AWS Configuration (Optional)

### Option 1: Use Default AWS Credentials

If you have AWS CLI configured:

```bash
aws configure
```

Then select "Use default AWS credentials" in the UI.

### Option 2: Provide Credentials in UI

1. Create a read-only IAM user
2. Attach the policy from `examples/iam_readonly_policy.json`
3. Generate access keys
4. Enter credentials in the StratusIQ UI

### Creating Read-Only IAM Policy

```bash
# Create the policy
aws iam create-policy \
  --policy-name StratusIQReadOnly \
  --policy-document file://examples/iam_readonly_policy.json

# Create a user
aws iam create-user --user-name stratusiq-scanner

# Attach the policy
aws iam attach-user-policy \
  --user-name stratusiq-scanner \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/StratusIQReadOnly

# Create access keys
aws iam create-access-key --user-name stratusiq-scanner
```

## Troubleshooting

### Import Errors

If you see import errors, make sure you're running from the `stratusiq` directory:

```bash
cd stratusiq
python -c "import sys; print(sys.path)"
```

### AWS Connection Issues

1. Check your credentials:
```bash
aws sts get-caller-identity
```

2. Verify IAM permissions:
```bash
aws ec2 describe-instances --max-results 1
```

3. Check region configuration

### Streamlit Issues

If Streamlit doesn't start:

```bash
# Check Streamlit version
streamlit --version

# Try running with explicit Python
python -m streamlit run app.py
```

## Development Mode

For development with auto-reload:

```bash
streamlit run app.py --server.runOnSave true
```

## Production Deployment

### Using Docker (Recommended)

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:

```bash
docker build -t stratusiq .
docker run -p 8501:8501 stratusiq
```

### Using Streamlit Cloud

1. Push code to GitHub
2. Go to https://share.streamlit.io
3. Deploy from your repository

## Environment Variables

You can set these environment variables:

```bash
export AWS_DEFAULT_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

## Next Steps

1. Run a scan on your infrastructure
2. Review the findings
3. Generate Terraform patches
4. Test fixes in non-production
5. Generate PDF reports for stakeholders

## Support

For issues or questions:
- Check the README.md
- Review the code documentation
- Open an issue on GitHub
