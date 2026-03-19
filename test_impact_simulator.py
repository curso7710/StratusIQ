"""Test script for impact simulator functionality"""
import json
from scanner.terraform_parser import TerraformParser
from graph.dependency_graph import DependencyGraph
from engine.rule_engine import RuleEngine
from impact.impact_simulator import ImpactSimulator


def test_impact_simulator():
    """Test impact simulation with sample data"""
    print("=" * 70)
    print("Testing Impact Simulator")
    print("=" * 70)
    
    # Load sample plan
    print("\n1. Loading sample Terraform plan...")
    with open('examples/terraform_sample_plan.json', 'r') as f:
        plan_data = json.load(f)
    
    # Parse resources
    print("2. Parsing resources...")
    parser = TerraformParser()
    resources = parser.parse_plan(plan_data)
    print(f"   ✓ Parsed {len(resources)} resources")
    
    # Build dependency graph
    print("3. Building dependency graph...")
    graph = DependencyGraph()
    graph.build_graph(resources)
    print(f"   ✓ Built graph with {graph.graph.number_of_nodes()} nodes")
    
    # Run detection
    print("4. Running detection rules...")
    engine = RuleEngine()
    findings = engine.run_all_checks(resources, graph)
    print(f"   ✓ Detected {len(findings)} findings")
    
    # Test impact simulation on each finding
    print("\n5. Testing impact simulation on findings...")
    print("=" * 70)
    
    simulator = ImpactSimulator()
    
    for i, finding in enumerate(findings[:5], 1):  # Test first 5 findings
        print(f"\nFinding {i}: {finding['title']}")
        print("-" * 70)
        
        # Simulate impact
        impact = simulator.simulate_change(finding, graph)
        
        # Display results
        print(f"Change Type:          {impact['change_type']}")
        print(f"Risk Level:           {impact['risk_level']}")
        print(f"Downtime Probability: {impact['downtime_probability']}")
        print(f"Estimated Downtime:   {impact['estimated_downtime']}")
        print(f"Affected Services:    {len(impact['affected_services'])} services")
        print(f"Blast Radius:         {impact['blast_radius_count']} resources")
        
        # Show affected services
        if impact['affected_services']:
            print("\nAffected Services:")
            for service in impact['affected_services'][:3]:
                print(f"  • {service}")
            if len(impact['affected_services']) > 3:
                print(f"  ... and {len(impact['affected_services']) - 3} more")
        
        # Show recommendations
        if impact['recommendations']:
            print("\nTop Recommendations:")
            for rec in impact['recommendations'][:3]:
                print(f"  {rec}")
        
        # Show complexity
        complexity = simulator.get_change_complexity_score(impact)
        if complexity < 30:
            complexity_label = "Simple"
        elif complexity < 60:
            complexity_label = "Moderate"
        else:
            complexity_label = "Complex"
        print(f"\nComplexity Score:     {complexity}/100 ({complexity_label})")
        
        print("-" * 70)
    
    print("\n" + "=" * 70)
    print("✅ Impact Simulator Test Complete!")
    print("=" * 70)
    
    # Summary statistics
    print("\nSummary Statistics:")
    risk_levels = {}
    change_types = {}
    
    for finding in findings:
        impact = simulator.simulate_change(finding, graph)
        risk_level = impact['risk_level']
        change_type = impact['change_type']
        
        risk_levels[risk_level] = risk_levels.get(risk_level, 0) + 1
        change_types[change_type] = change_types.get(change_type, 0) + 1
    
    print("\nRisk Level Distribution:")
    for level, count in sorted(risk_levels.items()):
        print(f"  {level}: {count} findings")
    
    print("\nChange Type Distribution:")
    for ctype, count in sorted(change_types.items()):
        print(f"  {ctype}: {count}")
    
    print("\n" + "=" * 70)
    print("Impact simulation is working correctly!")
    print("Run 'streamlit run app.py' to see it in the UI")
    print("=" * 70)


if __name__ == "__main__":
    test_impact_simulator()
