from typing import List, Optional, Any
import json

import ipaddress

class CIDRNode:
    def __init__(self, cidr: Optional[str] = None, parent: Optional['CIDRNode'] = None):
        self.cidr = cidr
        self.parent = parent
        self.chickenList: List[CIDRNode] = []

    @property
    def net(self):
        if self.cidr is None:
            return None
        return ipaddress.ip_network(self.cidr, strict=False)

    def contains_cidr(self, cidr_str: str) -> bool:
        """Return True if this node's CIDR contains the given cidr_str."""
        if self.cidr is None:
            return True  # root contains everything
        try:
            return self.net.supernet_of(ipaddress.ip_network(cidr_str, strict=False)) or self.cidr == cidr_str
        except Exception:
            return False

class CIDRTree:
    def __init__(self):
        self.rootCidrNode = CIDRNode()

    def formTreeFromCidrList(self, cidr_list: List[str]) -> None:
        # Clear any previous tree
        self.rootCidrNode.chickenList.clear()
        nodes = []
        # Create nodes for each CIDR
        for cidr_str in cidr_list:
            nodes.append(CIDRNode(cidr=cidr_str))
        # Sort by prefix length (shortest first)
        nodes.sort(key=lambda n: (n.net.version, n.net.prefixlen))
        # Build tree
        for idx, node in enumerate(nodes):
            parent_found = False
            # Check for parent among previous nodes
            for potential_parent in reversed(nodes[:idx]):
                # Only check supernet_of if both are same IP version
                if potential_parent.net.version != node.net.version:
                    continue
                if potential_parent.net.supernet_of(node.net):
                    node.parent = potential_parent
                    potential_parent.chickenList.append(node)
                    parent_found = True
                    break
            if not parent_found:
                node.parent = self.rootCidrNode
                self.rootCidrNode.chickenList.append(node)

    def getCidrTree(self, cidrString: str) -> Any:
        # Traverse from the given CIDR (or root if None) and build nested dict
        def node_to_dict(node):
            if not node.chickenList:
                return {}
            return {child.cidr: node_to_dict(child) for child in node.chickenList}
        if cidrString is None:
            return json.dumps({"null": node_to_dict(self.rootCidrNode)})
        # Find the node for cidrString
        def find_node(node, target):
            if node.cidr == target:
                return node
            # Only search children if target is within node's CIDR
            if not node.contains_cidr(target):
                return None
            for child in node.chickenList:
                found = find_node(child, target)
                if found:
                    return found
            return None
        start_node = find_node(self.rootCidrNode, cidrString)
        if start_node:
            return json.dumps({cidrString: node_to_dict(start_node)})
        return json.dumps({})
