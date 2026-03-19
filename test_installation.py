"""Test script to verify StratusIQ installation"""
import sys
import json

def test_imports():
    """Test all required imports"""
    print("Testing imports...")
    
    try:
        import streamlit
        print("✓ Streamlit imported successfully")
    except ImportError as e:
        print(f"✗ Streamlit import failed: {e}")
        return False
    
    try:
        import boto3
        print("✓ boto3 imported successfully")
    except ImportError as e:
        print(f"✗ boto3 import failed: {e}")
        return False
    
    try:
        import pandas
        print("✓ pandas imported successfully")
    except ImportError as e:
        print(f"✗ pandas import failed: {e}")
        return False
    
    try:
        import networkx
        print("✓ networkx imported successfully")
    except ImportError as e:
        print(f"✗ networkx import failed: {e}")
        return False
    
    try:
        import plotly
        print("✓ plotly imported successfully")
    except ImportError as e:
        print(f"✗ plotly import failed: {e}")
        return False
    
    try:
        from reportlab.lib.pagesizes import letter
        print("✓ reportlab imported successfully")
    except ImportError as e:
        print(f"✗ reportlab import failed: {e}")
        return False
    
    return True


def test_modules():
    """Test StratusIQ modules"""
    print("\nTesting StratusIQ modules...")
    
    try:
        from scanner.terraform_parser import TerraformParser
        print("✓ TerraformParser imported")
    except ImportError as e:
        print(f"✗ TerraformParser import failed: {e}")
        return False
    
    try:
        from scanner.aws_scanner import AWSScanner
        print("✓ AWSScanner imported")
    except ImportError as e:
        print(f"✗ AWSScanner import failed: {e}")
        return False
    
    try:
        from engine.rule_engine import RuleEngine
        print("✓ RuleEngine imported")
    except ImportError as e:
        print(f"✗ RuleEngine import failed: {e}")
        return False
    
    try:
        from graph.dependency_graph import DependencyGraph
        print("✓ DependencyGraph imported")
    except ImportError as e:
        print(f"✗ DependencyGraph import failed: {e}")
        return False
    
    try:
        from scoring.priority_scoring import PriorityScorer
        print("✓ PriorityScorer imported")
    except ImportError as e:
        print(f"✗ PriorityScorer import failed: {e}")
        return False
    
    return True


def test_sample_analysis():
    """Test analysis with sample data"""
    print("\nTesting sample analysis...")
    
    try:
        from scanner.terraform_parser import TerraformParser
        from engine.rule_engine import RuleEngine
        from graph.dependency_graph import DependencyGraph
        from scoring.priority_scoring import PriorityScorer
        
        # Load sample plan
        with open('examples/terraform_sample_plan.json', 'r') as f:
            plan_data = json.load(f)
        
        # Parse
        parser = TerraformParser()
        resources = parser.parse_plan(plan_data)
        print(f"✓ Parsed {len(resources)} resources")
        
        # Build graph
        graph = DependencyGraph()
        graph.build_graph(resources)
        print(f"✓ Built dependency graph")
        
        # Run detection
        engine = RuleEngine()
        findings = engine.run_all_checks(resources, graph)
        print(f"✓ Detected {len(findings)} findings")
        
        # Score findings
        scorer = PriorityScorer()
        findings = scorer.score_findings(findings)
        stats = scorer.get_summary_stats(findings)
        print(f"✓ Scored findings")
        
        # Display summary
        print("\nSample Analysis Results:")
        print(f"  Total Findings: {stats['total_findings']}")
        print(f"  Cost Findings: {stats['cost_findings']}")
        print(f"  Security Findings: {stats['security_findings']}")
        print(f"  Critical Issues: {stats['critical_findings']}")
        print(f"  Monthly Savings: ${stats['total_monthly_savings']:.2f}")
        
        if stats['total_findings'] > 0:
            print("\n✓ Sample analysis completed successfully!")
            return True
        else:
            print("\n✗ No findings detected (unexpected)")
            return False
            
    except Exception as e:
        print(f"✗ Sample analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("StratusIQ Installation Test")
    print("=" * 60)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import test failed. Please install requirements:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    # Test modules
    if not test_modules():
        print("\n❌ Module test failed. Check your installation.")
        sys.exit(1)
    
    # Test sample analysis
    if not test_sample_analysis():
        print("\n❌ Sample analysis failed.")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ All tests passed! StratusIQ is ready to use.")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run the application: streamlit run app.py")
    print("2. Upload examples/terraform_sample_plan.json")
    print("3. Review the findings and explore the features")
    print("\nFor more information, see README.md and USAGE_GUIDE.md")


if __name__ == "__main__":
    main()
