import ipaddress
import json
import sys
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from abc import ABC, abstractmethod
from ipaddress import ip_network, ip_address
from src.cidrtree import CIDRTree, CIDRNode

class CIDR:
    def __init__(self, cidr: str, cidr_type: str, tags: Optional[Dict[str, str]] = None):
        self.cidr = ipaddress.ip_network(cidr)
        self.cidr_str = str(self.cidr)  # Store string representation for easier comparison
        self.cidr_type = cidr_type
        self.tags = tags or {}
        self._tree: Optional[CIDRTree] = None
        self._parent: Optional['CIDR'] = None
        
    def __str__(self) -> str:
        return self.cidr_str
        
    def __repr__(self) -> str:
        return f"CIDR('{self.cidr_str}', '{self.cidr_type}')"
        
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, CIDR):
            return False
        return self.cidr == other.cidr
        
    def __hash__(self) -> int:
        return hash(self.cidr)

    def add_tag(self, key: str, value: str) -> None:
        """Add a tag to the CIDR"""
        self.tags[key] = value

    def remove_tag(self, key: str) -> None:
        """Remove a tag from the CIDR"""
        if key in self.tags:
            del self.tags[key]

    def get_tags(self) -> Dict[str, str]:
        """Get all tags for this CIDR"""
        return self.tags.copy()
    
    @property
    def parent(self) -> Optional['CIDR']:
        """Get the parent CIDR"""
        return self._parent
        
    @parent.setter
    def parent(self, parent: Optional['CIDR']) -> None:
        """Set the parent CIDR"""
        self._parent = parent
        
    @property
    def children(self) -> List['CIDR']:
        """Get child CIDRs"""
        if not self._tree:
            return []
            
        # Get the node for this CIDR
        node = self._tree.cidr_map.get(str(self.cidr))
        if not node:
            return []
            
        # Return the CIDR objects for the children
        return [child.cidr_obj for child in node.children if hasattr(child, 'cidr_obj')]
        
    def add_child(self, child: 'CIDR') -> None:
        """Add a child CIDR"""
        if not hasattr(self, '_children'):
            self._children = []
        self._children.append(child)
        child.parent = self

    def is_parent_of(self, other: 'CIDR') -> bool:
        """Check if this CIDR is a parent of another CIDR"""
        return self.cidr.supernet_of(other.cidr)
    
    def is_child_of(self, other: 'CIDR') -> bool:
        """Check if this CIDR is a child of another CIDR"""
        return self.cidr.subnet_of(other.cidr)
    
    @classmethod
    def build_hierarchy(cls, cidrs: List['CIDR']) -> None:
        """
        Build the hierarchy of CIDRs using CIDRTree
        
        Args:
            cidrs: List of CIDR objects to build hierarchy for
        """
        if not cidrs:
            return
            
        tree = CIDRTree()
        
        # First pass: add all CIDRs to the tree
        for cidr in cidrs:
            tree.add_cidr(cidr)
            
        # Second pass: set the tree reference and parent-child relationships
        for cidr in cidrs:
            cidr._tree = tree
            
            # Get the node for this CIDR
            node = tree.cidr_map.get(str(cidr.cidr))
            if node and node.parent and hasattr(node.parent, 'cidr_obj'):
                cidr._parent = node.parent.cidr_obj

class CloudProvider(ABC):
    @abstractmethod
    def load_cidrs(self) -> List[Dict[str, str]]:
        """Load CIDRs from the cloud provider"""
        pass

class TestProvider(CloudProvider):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def load_cidrs(self) -> Dict[str, Any]:
        """Load CIDRs from a local test file"""
        with open(self.file_path, 'r') as f:
            data = json.load(f)
            return data
            
    def get_cidr_blocks(self) -> List[CIDR]:
        """Get CIDR blocks as CIDR objects"""
        cidrs = []
        data = self.load_cidrs()
        for cidr_info in data.get('cidrs', []):
            cidr = CIDR(
                cidr=cidr_info['cidr'],
                cidr_type=cidr_info.get('type', 'VPC'),
                tags=cidr_info.get('tags', {})
            )
            cidrs.append(cidr)
        return cidrs


# AWSProvider has been moved to aws_provider.py

class IPAM:
    def __init__(self, cloud_provider: Optional[CloudProvider] = None):
        self.cidrs: Dict[str, CIDR] = {}
        self.cloud_provider = cloud_provider
        self.cidr_tree = CIDRTree()
        self._cidrs_loaded = False

    def _load_cidrs_from_file(self, file_path: str) -> List[CIDR]:
        """Helper to load CIDRs from a file and return a list of CIDR objects"""
        cidr_objects = []
        with open(file_path, 'r') as f:
            data = json.load(f)
            for cidr_data in data.get('cidrs', []):
                cidr = CIDR(
                    cidr=cidr_data['cidr'],
                    cidr_type='STATIC',
                    tags=cidr_data.get('tags', {})
                )
                cidr_objects.append(cidr)
        return cidr_objects

    def _get_all_cidrs(self) -> List[CIDR]:
        """Get all CIDRs from both static and cloud sources"""
        all_cidrs = list(self.cidrs.values())
        
        if self.cloud_provider:
            try:
                cloud_cidrs = self.cloud_provider.get_cidr_blocks()
                all_cidrs.extend(cloud_cidrs)
            except Exception as e:
                print(f"Warning: Failed to load cloud CIDRs: {e}", file=sys.stderr)
                
        return all_cidrs

    def _build_cidr_hierarchy(self) -> None:
        """Build the CIDR hierarchy using the more efficient build_tree_from_list"""
        all_cidrs = self._get_all_cidrs()
        self.cidr_tree.build_tree_from_list(all_cidrs)

    def load_static_cidrs(self, file_path: str) -> None:
        """Load CIDRs from a static file"""
        try:
            cidr_objects = self._load_cidrs_from_file(file_path)
            for cidr in cidr_objects:
                self.cidrs[str(cidr.cidr)] = cidr
            
            if self._cidrs_loaded:
                self._build_cidr_hierarchy()
                
        except Exception as e:
            print(f"Error loading static CIDRs: {e}", file=sys.stderr)
            raise

    def load_cloud_cidrs(self) -> None:
        """Load CIDRs from the configured cloud provider"""
        if not self.cloud_provider:
            return
            
        try:
            cidr_data = self.cloud_provider.load_cidrs()
            for cidr_info in cidr_data.get('cidrs', []):
                cidr = CIDR(
                    cidr=cidr_info['cidr'],
                    cidr_type='VPC',
                    tags=cidr_info.get('tags', {})
                )
                self.cidrs[str(cidr.cidr)] = cidr
            
            if self._cidrs_loaded:
                self._build_cidr_hierarchy()
                
        except Exception as e:
            print(f"Error loading cloud CIDRs: {e}", file=sys.stderr)
            raise

    def build_hierarchy(self) -> None:
        """Build or rebuild the CIDR hierarchy with all loaded CIDRs"""
        self._build_cidr_hierarchy()
        self._cidrs_loaded = True

    def get_all_cidrs(self) -> Dict[str, CIDR]:
        """Get all loaded CIDRs"""
        return self.cidrs.copy()  # Return a copy to prevent external modifications

    def get_cidr(self, cidr_str: str) -> Optional[CIDR]:
        """Get a specific CIDR by its string representation"""
        return self.cidrs.get(cidr_str)

    def find_containing_cidr(self, ip_address: str) -> Optional[CIDR]:
        """Find the smallest CIDR that contains the given IP address"""
        try:
            from ipaddress import ip_address as parse_ip
            ip = parse_ip(ip_address)
            
            # If we have a built tree, use it for more efficient lookup
            if self._cidrs_loaded:
                # Find all containing CIDRs and return the most specific one
                containing_cidrs = []
                for cidr in self.cidrs.values():
                    if ip in cidr.cidr:
                        containing_cidrs.append(cidr)
                
                if not containing_cidrs:
                    return None
                    
                # Return the CIDR with the longest prefix (most specific)
                return max(containing_cidrs, key=lambda c: c.cidr.prefixlen)
            else:
                # Fallback to linear search if hierarchy isn't built
                for cidr in self.cidrs.values():
                    if ip in cidr.cidr:
                        return cidr
                return None
                
        except ValueError:
            return None

    def get_cidr_tags(self, cidr: str) -> Dict[str, str]:
        """Get tags for a specific CIDR"""
        cidr_obj = self.cidrs.get(cidr)
        if cidr_obj:
            return cidr_obj.get_tags()
        return {}

    def find_cidrs_by_tag(self, key: str, value: str) -> List[CIDR]:
        """Find CIDRs with specific tag"""
        return [cidr for cidr in self.cidrs.values() 
               if cidr.tags.get(key) == value]

    def get_child_cidrs(self, parent_cidr: str) -> List[CIDR]:
        """Get direct child CIDRs of a given CIDR"""
        parent = self.cidrs.get(parent_cidr)
        if not parent:
            return []

        # Get all potential children
        potential_children = [cidr for cidr in self.cidrs.values() 
                            if cidr.is_child_of(parent) and str(cidr.cidr) != parent_cidr]
        
        # Filter out grandchild CIDRs
        direct_children = []
        for cidr in potential_children:
            # Check if this CIDR is a direct child (not a grandchild)
            is_direct = True
            for other in potential_children:
                if cidr != other and cidr.is_child_of(other):
                    is_direct = False
                    break
            if is_direct:
                direct_children.append(cidr)
        
        return direct_children

    def find_available_cidr(self, parent_cidr: str, prefix_length: int) -> Optional[CIDR]:
        """Find an available CIDR with specified prefix length under a parent CIDR"""
        parent = self.cidrs.get(parent_cidr)
        if not parent:
            return None

        # Get all existing child CIDRs
        existing_cidrs = set(str(c.cidr) for c in self.get_child_cidrs(parent_cidr))

        # Generate all possible CIDRs of the requested prefix length
        possible_cidrs = list(parent.cidr.subnets(new_prefix=prefix_length))

        # Find the first available CIDR
        for possible_cidr in possible_cidrs:
            if str(possible_cidr) not in existing_cidrs:
                return CIDR(
                    cidr=str(possible_cidr),
                    cidr_type='STATIC',
                    tags={'status': 'available'}
                )
        return None

# Example usage:
if __name__ == "__main__":
    # Create IPAM with test provider
    test_provider = TestProvider('test_cidrs.json')
    ipam = IPAM(cloud_provider=test_provider)
    
    # Load static CIDRs from file
    ipam.load_static_cidrs('static_cidrs.json')
    
    # Load test CIDRs
    ipam.load_cloud_cidrs()
    
    # Example queries
    print("\nAvailable /24 CIDRs under 10.0.0.0/8:")
    available_cidr = ipam.find_available_cidr("10.0.0.0/8", 24)
    if available_cidr:
        print(f"Found available CIDR: {available_cidr.cidr}")
    
    print("\nChild CIDRs of 10.0.0.0/8:")
    for cidr in ipam.get_child_cidrs("10.0.0.0/8"):
        print(f"- {cidr.cidr} ({cidr.cidr_type})")
    
    print("\nCIDRs tagged with 'environment=prod':")
    for cidr in ipam.find_cidrs_by_tag("environment", "prod"):
        print(f"- {cidr.cidr} ({cidr.cidr_type})")