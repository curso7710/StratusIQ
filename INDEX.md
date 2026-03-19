# StratusIQ Documentation Index

## 📖 Quick Navigation

### 🚀 Getting Started (Start Here!)
1. **[QUICK_START.md](QUICK_START.md)** - 5-minute setup and demo
2. **[SETUP.md](SETUP.md)** - Detailed installation guide
3. **[README.md](README.md)** - Project overview and features

### 📚 User Guides
4. **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Complete usage instructions
5. **[FEATURES.md](FEATURES.md)** - Feature checklist

### 🏗️ Technical Documentation
6. **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and architecture
7. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Executive summary
8. **[IMPACT_SIMULATION.md](IMPACT_SIMULATION.md)** - Change impact simulation guide

## 📋 Documentation by Purpose

### For First-Time Users
Start with these in order:
1. **QUICK_START.md** - Get running in 5 minutes
2. **README.md** - Understand what StratusIQ does
3. **USAGE_GUIDE.md** - Learn how to use each feature

### For Installation
- **SETUP.md** - Step-by-step installation
- **requirements.txt** - Python dependencies
- **test_installation.py** - Verify installation

### For Daily Use
- **USAGE_GUIDE.md** - How to use each page
- **examples/terraform_sample_plan.json** - Sample data
- **examples/iam_readonly_policy.json** - AWS policy

### For Developers
- **ARCHITECTURE.md** - System design
- **FEATURES.md** - Implementation checklist
- **Code comments** - Inline documentation

### For Management
- **PROJECT_SUMMARY.md** - Executive overview
- **FEATURES.md** - Capabilities list
- **README.md** - Business value

## 📁 File Organization

### Core Application
```
app.py                  - Main Streamlit application
config.py              - Configuration and settings
requirements.txt       - Python dependencies
```

### Source Code Modules
```
scanner/               - Input parsers (Terraform, AWS)
engine/                - Detection rules (cost, security)
graph/                 - Dependency analysis
scoring/               - Priority calculation
fixes/                 - Remediation generation
llm/                   - Explanation engine
dashboard/             - UI components
report/                - PDF generation
utils/                 - Helper utilities
```

### Documentation
```
README.md              - Project overview
QUICK_START.md         - 5-minute guide
SETUP.md               - Installation
USAGE_GUIDE.md         - How-to guide
ARCHITECTURE.md        - Technical docs
FEATURES.md            - Feature list
PROJECT_SUMMARY.md     - Executive summary
IMPACT_SIMULATION.md   - Impact simulation guide
INDEX.md               - This file
```

### Examples and Tests
```
examples/              - Sample data files
test_installation.py   - Installation test
.gitignore            - Git ignore rules
```

## 🎯 Documentation by Role

### Cloud Engineer
**Goal:** Optimize infrastructure
**Read:**
1. QUICK_START.md
2. USAGE_GUIDE.md (Workflows section)
3. README.md (Detection Rules)

### Security Engineer
**Goal:** Fix security issues
**Read:**
1. QUICK_START.md
2. USAGE_GUIDE.md (Security Audit workflow)
3. FEATURES.md (Security Rules)

### DevOps Engineer
**Goal:** Integrate into pipeline
**Read:**
1. SETUP.md
2. ARCHITECTURE.md
3. examples/iam_readonly_policy.json

### Developer
**Goal:** Extend or customize
**Read:**
1. ARCHITECTURE.md
2. FEATURES.md
3. Code in scanner/, engine/, fixes/

### Manager
**Goal:** Understand value
**Read:**
1. PROJECT_SUMMARY.md
2. README.md
3. FEATURES.md

## 📖 Documentation Content Guide

### QUICK_START.md
- 5-minute setup
- Demo with sample data
- Expected results
- Common commands
- Troubleshooting

### README.md
- Feature overview
- Quick start
- Usage examples
- Detection rules
- Architecture diagram
- Requirements

### SETUP.md
- Prerequisites
- Installation steps
- AWS configuration
- Troubleshooting
- Production deployment
- Environment variables

### USAGE_GUIDE.md
- Page-by-page guide
- Common workflows
- Understanding findings
- Best practices
- Tips and tricks
- Advanced usage

### ARCHITECTURE.md
- System overview
- Component details
- Data flow
- Configuration
- Security design
- Extensibility
- Performance

### FEATURES.md
- Complete feature checklist
- Implementation status
- Statistics
- Production-ready features
- Future enhancements

### PROJECT_SUMMARY.md
- Executive overview
- What was built
- Key features
- Technical highlights
- Deliverables
- Next steps

## 🔍 Find Information By Topic

### Installation
- QUICK_START.md (Quick install)
- SETUP.md (Detailed install)
- test_installation.py (Verify)

### Usage
- USAGE_GUIDE.md (Complete guide)
- README.md (Quick examples)
- QUICK_START.md (Demo)

### Features
- FEATURES.md (Complete list)
- README.md (Overview)
- PROJECT_SUMMARY.md (Summary)

### Architecture
- ARCHITECTURE.md (Detailed)
- PROJECT_SUMMARY.md (Overview)
- Code comments (Implementation)

### Configuration
- config.py (Settings)
- SETUP.md (AWS setup)
- examples/iam_readonly_policy.json (IAM)

### Troubleshooting
- SETUP.md (Installation issues)
- USAGE_GUIDE.md (Usage issues)
- QUICK_START.md (Common problems)

### Examples
- examples/terraform_sample_plan.json (Sample data)
- examples/iam_readonly_policy.json (IAM policy)
- QUICK_START.md (Demo walkthrough)

## 📊 Documentation Statistics

- **Total Documentation Files:** 9
- **Total Pages:** 60+ (estimated)
- **Total Words:** 18,000+ (estimated)
- **Code Comments:** Extensive
- **Examples:** 2 files
- **Guides:** 5 user guides
- **Technical Docs:** 3 files

## 🎓 Learning Path

### Beginner Path
1. Read QUICK_START.md
2. Run test_installation.py
3. Try the demo
4. Read README.md
5. Explore USAGE_GUIDE.md

### Intermediate Path
1. Complete Beginner Path
2. Read SETUP.md
3. Configure AWS scanning
4. Read ARCHITECTURE.md
5. Review code structure

### Advanced Path
1. Complete Intermediate Path
2. Study ARCHITECTURE.md in detail
3. Review source code
4. Read FEATURES.md
5. Plan customizations

## 🔗 External Resources

### Technologies Used
- **Streamlit:** https://docs.streamlit.io/
- **boto3:** https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
- **NetworkX:** https://networkx.org/documentation/stable/
- **Plotly:** https://plotly.com/python/
- **ReportLab:** https://www.reportlab.com/docs/reportlab-userguide.pdf

### AWS Documentation
- **Terraform JSON:** https://www.terraform.io/docs/internals/json-format.html
- **IAM Policies:** https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html
- **CloudWatch:** https://docs.aws.amazon.com/cloudwatch/

## 💡 Tips for Reading

### First Time?
Start with QUICK_START.md → README.md → USAGE_GUIDE.md

### Need to Install?
Go to SETUP.md

### Want to Use?
Check USAGE_GUIDE.md

### Need Technical Details?
Read ARCHITECTURE.md

### Want to Extend?
Study ARCHITECTURE.md + source code

### Presenting to Management?
Use PROJECT_SUMMARY.md

## 📞 Getting Help

### Documentation Issues
- Check INDEX.md (this file)
- Review relevant guide
- Check code comments

### Installation Issues
- Read SETUP.md troubleshooting
- Run test_installation.py
- Check requirements.txt

### Usage Questions
- Read USAGE_GUIDE.md
- Check QUICK_START.md
- Review examples/

### Technical Questions
- Read ARCHITECTURE.md
- Review source code
- Check FEATURES.md

## ✅ Documentation Checklist

- ✅ Quick start guide
- ✅ Installation guide
- ✅ Usage guide
- ✅ Architecture documentation
- ✅ Feature list
- ✅ Project summary
- ✅ Code comments
- ✅ Example files
- ✅ Navigation index (this file)

## 🎯 Next Steps

1. **New User?** → Start with QUICK_START.md
2. **Installing?** → Go to SETUP.md
3. **Using?** → Read USAGE_GUIDE.md
4. **Developing?** → Study ARCHITECTURE.md
5. **Presenting?** → Use PROJECT_SUMMARY.md

---

**Welcome to StratusIQ! Choose your path above and get started. 🚀**
