import os
import sys

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.cidrtree import CIDRTree, tree

def main():
    # Example CIDRs
    cidrs = [
        "10.0.0.0/8",
        "10.1.0.0/16",
        "10.1.1.0/24",
        "10.1.2.0/24",
        "10.2.0.0/16",
        "192.168.1.0/24"
    ]
    
    # Build and print the tree
    print("Full CIDR tree:")
    cidr_tree = CIDRTree()
    cidr_tree.build_tree(cidrs)
    print(cidr_tree.print_tree())
    
    # Print a subtree
    print("\nSubtree for 10.0.0.0/8:")
    print(tree("10.0.0.0/8", cidrs))

if __name__ == "__main__":
    main()
