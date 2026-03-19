"""Dependency graph builder using networkx"""
import networkx as nx
from typing import Dict, List
from utils.logging_utils import setup_logger

logger = setup_logger(__name__)


class DependencyGraph:
    """Build and analyze resource dependency graph"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
    
    def build_graph(self, resources: List[Dict]):
        """Build dependency graph from resources"""
        self.graph.clear()
        
        # Add all resources as nodes
        for resource in resources:
            self.graph.add_node(
                resource['resource_id'],
                type=resource['type'],
                config=resource['config']
            )
        
        # Add edges based on relationships
        for resource in resources:
            source = resource['resource_id']
            for target in resource.get('relationships', []):
                if self.graph.has_node(target):
                    self.graph.add_edge(source, target)
        
        logger.info(f"Built graph with {self.graph.number_of_nodes()} nodes "
                   f"and {self.graph.number_of_edges()} edges")
    
    def get_blast_radius(self, resource_id: str) -> List[str]:
        """Get all resources affected by changes to this resource"""
        if not self.graph.has_node(resource_id):
            return []
        
        # Get all descendants (resources that depend on this one)
        descendants = nx.descendants(self.graph, resource_id)
        
        # Get all ancestors (resources this one depends on)
        ancestors = nx.ancestors(self.graph, resource_id)
        
        # Combine for full blast radius
        blast_radius = list(descendants.union(ancestors))
        
        return blast_radius
    
    def get_connected_resources(self, resource_id: str) -> List[str]:
        """Get directly connected resources"""
        if not self.graph.has_node(resource_id):
            return []
        
        # Get predecessors and successors
        predecessors = list(self.graph.predecessors(resource_id))
        successors = list(self.graph.successors(resource_id))
        
        return predecessors + successors
    
    def get_graph_data(self) -> Dict:
        """Get graph data for visualization"""
        nodes = []
        edges = []
        
        for node in self.graph.nodes(data=True):
            nodes.append({
                "id": node[0],
                "type": node[1].get('type', 'unknown'),
                "label": node[0]
            })
        
        for edge in self.graph.edges():
            edges.append({
                "source": edge[0],
                "target": edge[1]
            })
        
        return {"nodes": nodes, "edges": edges}
    
    def get_resource_info(self, resource_id: str) -> Dict:
        """Get resource information from graph"""
        if not self.graph.has_node(resource_id):
            return {}
        
        node_data = self.graph.nodes[resource_id]
        
        return {
            "resource_id": resource_id,
            "type": node_data.get('type'),
            "config": node_data.get('config'),
            "connected_resources": self.get_connected_resources(resource_id),
            "blast_radius": self.get_blast_radius(resource_id)
        }
