from typing import Dict, List, Optional, Set, Tuple, Any, Union
from ipaddress import ip_network, ip_network as ip_network_fn, IPv4Network, IPv6Network
from dataclasses import dataclass, field
from collections import defaultdict, deque
import sys

class CIDRNode:
    """Represents a node in the CIDR tree"""
    def __init__(self, cidr: str, cidr_obj: Any = None):
        self.cidr = cidr
        self.cidr_obj = cidr_obj
        self.children: List['CIDRNode'] = []
        self.parent: Optional['CIDRNode'] = None
        self._network = ip_network(cidr)
    
    def is_parent_of(self, other_node: 'CIDRNode') -> bool:
        """Check if this node is a parent of the other node"""
        try:
            parent_net = ip_network(self.cidr)
            child_net = ip_network(other_node.cidr)
            
            if parent_net.version != child_net.version:
                return False
                
            return (parent_net.network_address <= child_net.network_address and 
                   parent_net.broadcast_address >= child_net.broadcast_address and
                   parent_net.prefixlen < child_net.prefixlen)
        except Exception:
            return False
    
    @property
    def network(self):
        return self._network
    
    def is_parent_of(self, other: 'CIDRNode') -> bool:
        """Check if this node is a parent of another node"""
        if self._network.version != other._network.version:
            return False
        return (
            self._network.network_address <= other._network.network_address and
            self._network.broadcast_address >= other._network.broadcast_address and
            self._network.prefixlen < other._network.prefixlen
        )

class CIDRTree:
    """Manages a tree of CIDRs for hierarchical visualization"""
    
    def __init__(self):
        self.roots: List[CIDRNode] = []
        self.cidr_map: Dict[str, CIDRNode] = {}
    
    def add_cidr(self, cidr: Union[str, Any]) -> None:
        """Add a CIDR to the tree"""
        if hasattr(cidr, 'cidr'):  # If it's a CIDR object from ipam.py
            cidr_str = str(cidr.cidr)
            cidr_obj = cidr
        else:  # It's a string
            cidr_str = str(cidr)
            cidr_obj = None
            
        if cidr_str in self.cidr_map:
            return
            
        try:
            node = CIDRNode(cidr_str, cidr_obj)
            
            # First, find and remove any existing nodes that are now children of this one
            children_to_remove = []
            for existing_cidr, existing_node in list(self.cidr_map.items()):
                try:
                    if node.is_parent_of(existing_node):
                        children_to_remove.append(existing_node)
                except Exception:
                    continue
            
            # Add the new node
            self.cidr_map[cidr_str] = node
            
            # Find parent for the new node
            parent = self._find_parent(cidr_str)
            
            if parent is None:
                # This is a new root
                self.roots.append(node)
            else:
                # Add as child to the parent
                parent.children.append(node)
                node.parent = parent
                
                # If this node was a root, remove it
                if node in self.roots:
                    self.roots.remove(node)
            
            # Reparent any children
            for child in children_to_remove:
                if child.parent:
                    child.parent.children.remove(child)
                node.children.append(child)
                child.parent = node
                # If child was a root, remove it
                if child in self.roots:
                    self.roots.remove(child)
                    
        except ValueError as e:
            print(f"Error adding CIDR {cidr_str}: {e}", file=sys.stderr)
            if cidr_str in self.cidr_map:
                del self.cidr_map[cidr_str]
    
    def _find_parent(self, cidr: str) -> Optional[CIDRNode]:
        """Find the immediate parent CIDR in the tree"""
        try:
            network = ip_network(cidr)
            parent = None
            
            for existing_cidr, existing_node in self.cidr_map.items():
                try:
                    if existing_cidr == cidr:
                        continue  # Skip self
                        
                    existing_network = ip_network(existing_cidr)
                    
                    # Skip if not the same address family
                    if existing_network.version != network.version:
                        continue
                        
                    # Check if existing CIDR is a direct parent
                    if (existing_network.network_address <= network.network_address and
                        existing_network.broadcast_address >= network.broadcast_address and
                        existing_network.prefixlen < network.prefixlen):
                        
                        # If we haven't found a parent yet, or this one is more specific
                        if parent is None or ip_network(parent.cidr).prefixlen < existing_network.prefixlen:
                            parent = existing_node
                        
                except ValueError:
                    # Skip invalid CIDRs
                    continue
                    
            return parent
            
        except ValueError as e:
            print(f"Error processing CIDR {cidr}: {e}", file=sys.stderr)
            return None
    
    def build_tree(self, cidrs: List[Union[str, Any]]) -> None:
        """
        Build the tree from a list of CIDRs (maintained for backward compatibility)
        
        Args:
            cidrs: List of CIDR strings or objects
        """
        self.build_tree_from_list(cidrs)
    
    def build_tree_from_list(self, cidrs: List[Union[str, Any]]) -> None:
        """
        Optimized tree building when all CIDRs are provided upfront.
        Sorts by prefix length (shorter masks first) for efficient hierarchy construction.
        
        Args:
            cidrs: List of CIDR strings or objects
        """
        if not cidrs:
            return
            
        try:
            # Convert all CIDRs to string representation and sort by prefix length (shorter first)
            cidr_entries = []
            for cidr in cidrs:
                if hasattr(cidr, 'cidr'):  # CIDR object
                    cidr_str = str(cidr.cidr)
                    cidr_entries.append((cidr_str, cidr, ip_network(cidr_str).prefixlen))
                else:  # String
                    cidr_str = str(cidr)
                    cidr_entries.append((cidr_str, cidr, ip_network(cidr_str).prefixlen))
            
            # Sort by prefix length (shorter first) and then by network address
            cidr_entries.sort(key=lambda x: (x[2], ip_network(x[0]).network_address))
            
            # Clear existing tree
            self.roots = []
            self.cidr_map = {}
            
            # Add CIDRs in order (from shortest to longest prefix)
            for cidr_str, cidr_obj, _ in cidr_entries:
                if cidr_str in self.cidr_map:
                    continue
                    
                node = CIDRNode(cidr_str, cidr_obj if hasattr(cidr_obj, 'cidr') else None)
                self.cidr_map[cidr_str] = node
                
                # Find the best parent
                parent = None
                parent_prefix_len = -1
                
                for existing_cidr, existing_node in self.cidr_map.items():
                    if existing_cidr == cidr_str:
                        continue
                        
                    try:
                        existing_net = ip_network(existing_cidr)
                        current_net = ip_network(cidr_str)
                        
                        if (existing_net.version == current_net.version and
                            existing_net.network_address <= current_net.network_address and
                            existing_net.broadcast_address >= current_net.broadcast_address and
                            existing_net.prefixlen < current_net.prefixlen and
                            existing_net.prefixlen > parent_prefix_len):
                            
                            parent = existing_node
                            parent_prefix_len = existing_net.prefixlen
                            
                    except ValueError:
                        continue
                
                if parent is not None:
                    parent.children.append(node)
                    node.parent = parent
                else:
                    self.roots.append(node)
                    
        except Exception as e:
            print(f"Error building tree from list: {e}", file=sys.stderr)
            raise
    
    def print_tree(self, root_cidr: Optional[str] = None) -> str:
        """Print the tree in a tree-like structure"""
        result = []
        
        if root_cidr:
            if root_cidr not in self.cidr_map:
                return f"CIDR {root_cidr} not found in tree\n"
            self._print_node(self.cidr_map[root_cidr], "", True, result)
        else:
            # Sort roots by network address for consistent output
            sorted_roots = sorted(self.roots, key=lambda x: ip_network(x.cidr))
            for i, root in enumerate(sorted_roots):
                is_last = (i == len(sorted_roots) - 1)
                self._print_node(root, "", is_last, result)
        
        return "\n".join(result)
    
    def _print_node(self, node: CIDRNode, prefix: str, is_last: bool, result: List[str], depth: int = 0, max_depth: int = 10) -> None:
        """Recursively print a node and its children"""
        if depth > max_depth:
            result.append(f"{prefix}└── ... (max depth reached)")
            return
            
        connector = "└── " if is_last else "├── "
        result.append(f"{prefix}{connector}{node.cidr}")
        
        # Update prefix for children
        new_prefix = prefix + ("    " if is_last else "│   ")
        
        # Sort children by network address for consistent output
        try:
            sorted_children = sorted(node.children, key=lambda x: ip_network(x.cidr))
            
            # Print children
            for i, child in enumerate(sorted_children):
                is_last_child = (i == len(sorted_children) - 1)
                self._print_node(child, new_prefix, is_last_child, result, depth + 1, max_depth)
        except Exception as e:
            result.append(f"{new_prefix}└── [Error: {str(e)}]")

def tree(cidr: str, cidrs: List[Union[str, Any]]) -> str:
    """
    Print a tree of CIDRs starting from the specified CIDR
    
    Args:
        cidr: The root CIDR to start the tree from
        cidrs: List of CIDR strings or objects to include in the tree
        
    Returns:
        String representation of the CIDR tree
    """
    tree = CIDRTree()
    tree.build_tree(cidrs)
    return tree.print_tree(cidr)

def build_cidr_tree(cidrs: List[Union[str, Any]]) -> CIDRTree:
    """
    Build a CIDR tree from a list of CIDR strings or objects
    
    Args:
        cidrs: List of CIDR strings or objects
        
    Returns:
        CIDRTree object
    """
    tree = CIDRTree()
    tree.build_tree(cidrs)
    return tree

def main():
    # Example CIDRs (note: order doesn't matter for build_tree_from_list)
    cidrs = [
        "10.1.1.0/24",  # More specific first
        "10.1.2.0/24",
        "10.1.0.0/16",
        "10.0.0.0/8",   # Less specific later
        "10.2.0.0/16",
        "192.168.1.0/24"
    ]
    
    # Test 1: Using build_tree_from_list (optimized for initial build)
    print("\n=== Test 1: Using build_tree_from_list ===")
    tree1 = CIDRTree()
    tree1.build_tree_from_list(cidrs)
    print("Full tree:")
    print(tree1.print_tree())
    
    # Test 2: Using add_cidr (for incremental updates)
    print("\n=== Test 2: Using add_cidr (incremental) ===")
    tree2 = CIDRTree()
    for cidr in cidrs:
        tree2.add_cidr(cidr)
    print("Full tree:")
    print(tree2.print_tree())
    
    # Test 3: Using the convenience function
    print("\n=== Test 3: Using build_cidr_tree function ===")
    tree3 = build_cidr_tree(cidrs)
    print("Full tree:")
    print(tree3.print_tree())
    
    # Print a subtree
    print("\n=== Subtree for 10.0.0.0/8 ===")
    print(tree("10.0.0.0/8", cidrs))
    
    # Print another subtree
    print("\n=== Subtree for 10.1.0.0/16 ===")
    print(tree("10.1.0.0/16", cidrs))

if __name__ == "__main__":
    main()
