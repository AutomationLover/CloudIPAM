# CIDRTree Module

This module provides a simple and efficient way to build and traverse hierarchical trees of IPv4/IPv6 CIDR blocks in Python.

## Main Components

- **CIDRNode**: Represents a single CIDR block in the tree. Each node knows its CIDR string, parent, and children (`chickenList`). It provides:
  - `net` property: Returns the parsed ipaddress network object.
  - `contains_cidr(cidr_str)`: Checks if a given CIDR string is within this node's range.

- **CIDRTree**: Manages the entire CIDR hierarchy.
  - `rootCidrNode`: The root node (has no CIDR, contains all).
  - `formTreeFromCidrList(cidr_list)`: Builds the tree from a flat list of CIDR strings, automatically setting parent-child relationships.
  - `getCidrTree(cidrString)`: Returns a nested JSON representation of the subtree starting from the specified CIDR (or the whole tree if `None`).

## Features
- Supports both IPv4 and IPv6 CIDRs.
- Efficient parent-child lookup and containment checks.
- Suitable for network management, IPAM, and visualization tasks.

## Example Usage
```python
from cidrtree import CIDRTree

tree = CIDRTree()
tree.formTreeFromCidrList([
    "10.0.0.0/8", "10.1.0.0/16", "10.1.1.0/24", "10.1.1.128/25"
])
print(tree.getCidrTree(None))
```

## Tests
See `test/test_cidrtree.py` for comprehensive unit tests covering IPv4, IPv6, and mixed scenarios.
