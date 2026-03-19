"""Configuration settings for StratusIQ"""

# AWS Pricing (simplified monthly estimates in USD)
EC2_PRICING = {
    "t2.micro": 8.47,
    "t2.small": 16.79,
    "t2.medium": 33.58,
    "t3.micro": 7.59,
    "t3.small": 15.18,
    "t3.medium": 30.37,
    "m5.large": 70.08,
    "m5.xlarge": 140.16,
    "m5.2xlarge": 280.32,
    "m5.4xlarge": 560.64,
    "c5.large": 62.05,
    "c5.xlarge": 124.10,
    "r5.large": 91.98,
    "r5.xlarge": 183.96,
}

EBS_PRICING_PER_GB = 0.10  # per GB per month
ELASTIC_IP_PRICING = 3.65  # per month when not attached
SNAPSHOT_PRICING_PER_GB = 0.05  # per GB per month

# Severity weights for scoring
SEVERITY_SCORES = {
    "critical": 100,
    "high": 75,
    "medium": 50,
    "low": 25,
}

# Priority scoring weights
COST_SAVINGS_WEIGHT = 1.0
SEVERITY_WEIGHT = 0.5
CHANGE_RISK_WEIGHT = 0.3

# Risk scores
RISK_SCORES = {
    "low": 10,
    "medium": 30,
    "high": 50,
}

# Impact simulation settings
IMPACT_RISK_PENALTY = 20  # Additional penalty for high-risk changes in priority scoring

# Change complexity thresholds
COMPLEXITY_SIMPLE = 30
COMPLEXITY_MODERATE = 60
COMPLEXITY_COMPLEX = 100

# CPU thresholds
IDLE_CPU_THRESHOLD = 10.0
LOW_CPU_THRESHOLD = 30.0

# Risky ports for security groups
RISKY_PORTS = [22, 3389, 5432, 3306, 1433, 27017, 6379, 9200]
