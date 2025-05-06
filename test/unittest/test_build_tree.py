#!/usr/bin/env python3
"""
Test script for build_tree_from_list functionality in cidrtree.py
"""
import os
import sys
import unittest

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.cidrtree import CIDRTree, build_cidr_tree

class TestBuildTreeFromList(unittest.TestCase):    
    def test_basic_tree_construction(self):
        """Test basic tree construction with a simple hierarchy"""
        cidrs = [
            "10.0.0.0/8",
            "10.1.0.0/16",
            "10.1.1.0/24",
            "10.2.0.0/16",
            "192.168.1.0/24"
        ]
        
        tree = CIDRTree()
        tree.build_tree_from_list(cidrs)
        
        # Verify root nodes
        root_cidrs = [node.cidr for node in tree.roots]
        self.assertIn("10.0.0.0/8", root_cidrs)
        self.assertIn("192.168.1.0/24", root_cidrs)
        
        # Verify hierarchy
        node_10 = tree.cidr_map["10.0.0.0/8"]
        self.assertEqual(len(node_10.children), 2)  # Should have 2 children
        
        child_cidrs = [child.cidr for child in node_10.children]
        self.assertIn("10.1.0.0/16", child_cidrs)
        self.assertIn("10.2.0.0/16", child_cidrs)
        
        node_10_1 = tree.cidr_map["10.1.0.0/16"]
        self.assertEqual(len(node_10_1.children), 1)  # Should have 1 child
        self.assertEqual(node_10_1.children[0].cidr, "10.1.1.0/24")

    def test_multi_level_hierarchy(self):
        """Test tree construction with multiple levels of hierarchy"""
        cidrs = [
            "10.0.0.0/8",
            "10.1.0.0/16",
            "10.1.1.0/24",
            "10.1.1.128/25",
            "10.1.1.0/26",
            "10.2.0.0/16",
            "10.2.1.0/24",
            "10.2.1.0/28",
            "192.168.0.0/16",
            "192.168.1.0/24"
        ]
        
        tree = CIDRTree()
        tree.build_tree_from_list(cidrs)
        
        # Verify root nodes
        root_cidrs = [node.cidr for node in tree.roots]
        self.assertIn("10.0.0.0/8", root_cidrs)
        self.assertIn("192.168.0.0/16", root_cidrs)
        
        # Verify 10.0.0.0/8 hierarchy
        node_10 = tree.cidr_map["10.0.0.0/8"]
        self.assertEqual(len(node_10.children), 2)  # 10.1.0.0/16 and 10.2.0.0/16
        
        # Verify 10.1.0.0/16 hierarchy
        node_10_1 = tree.cidr_map["10.1.0.0/16"]
        self.assertEqual(len(node_10_1.children), 1)  # 10.1.1.0/24
        
        # Verify 10.1.1.0/24 hierarchy
        node_10_1_1 = tree.cidr_map["10.1.1.0/24"]
        self.assertEqual(len(node_10_1_1.children), 2)  # 10.1.1.128/25 and 10.1.1.0/26
        
        # Verify 10.2.0.0/16 hierarchy
        node_10_2 = tree.cidr_map["10.2.0.0/16"]
        self.assertEqual(len(node_10_2.children), 1)  # 10.2.1.0/24
        
        # Verify 10.2.1.0/24 hierarchy
        node_10_2_1 = tree.cidr_map["10.2.1.0/24"]
        self.assertEqual(len(node_10_2_1.children), 1)  # 10.2.1.0/28
        
        # Verify 192.168.0.0/16 hierarchy
        node_192 = tree.cidr_map["192.168.0.0/16"]
        self.assertEqual(len(node_192.children), 1)  # 192.168.1.0/24

    def test_non_contiguous_cidrs(self):
        """Test with non-contiguous CIDRs"""
        cidrs = [
            "172.16.0.0/12",
            "172.16.1.0/24",
            "172.17.0.0/16",
            "192.168.0.0/16",
            "192.168.1.0/24",
            "192.168.2.0/24"
        ]
        
        tree = CIDRTree()
        tree.build_tree_from_list(cidrs)
        
        # Verify root nodes
        root_cidrs = [node.cidr for node in tree.roots]
        self.assertIn("172.16.0.0/12", root_cidrs)
        self.assertIn("192.168.0.0/16", root_cidrs)
        
        # Verify 172.16.0.0/12 hierarchy
        node_172 = tree.cidr_map["172.16.0.0/12"]
        self.assertEqual(len(node_172.children), 2)  # 172.16.1.0/24 and 172.17.0.0/16
        
        # Verify 192.168.0.0/16 hierarchy
        node_192 = tree.cidr_map["192.168.0.0/16"]
        self.assertEqual(len(node_192.children), 2)  # 192.168.1.0/24 and 192.168.2.0/24

    def test_ipv4_and_ipv6_mixed(self):
        """Test with both IPv4 and IPv6 addresses"""
        cidrs = [
            "10.0.0.0/8",
            "10.1.0.0/16",
            "2001:db8::/32",
            "2001:db8:1::/48",
            "2001:db8:1:1::/64"
        ]
        
        tree = CIDRTree()
        tree.build_tree_from_list(cidrs)
        
        # Verify root nodes
        root_cidrs = [node.cidr for node in tree.roots]
        self.assertIn("10.0.0.0/8", root_cidrs)
        self.assertIn("2001:db8::/32", root_cidrs)
        
        # Verify IPv4 hierarchy
        node_10 = tree.cidr_map["10.0.0.0/8"]
        self.assertEqual(len(node_10.children), 1)  # 10.1.0.0/16
        
        # Verify IPv6 hierarchy
        node_2001 = tree.cidr_map["2001:db8::/32"]
        self.assertEqual(len(node_2001.children), 1)  # 2001:db8:1::/48
        
        node_2001_1 = tree.cidr_map["2001:db8:1::/48"]
        self.assertEqual(len(node_2001_1.children), 1)  # 2001:db8:1:1::/64
    
    def test_out_of_order_cidrs(self):
        """Test that CIDRs are properly ordered by prefix length"""
        cidrs = [
            "10.1.1.0/24",  # Most specific first
            "10.1.0.0/16",
            "10.0.0.0/8",   # Least specific last
            "10.2.0.0/16"
        ]
        
        tree = CIDRTree()
        tree.build_tree_from_list(cidrs)
        
        # Verify the tree structure is still correct
        self.assertIn("10.0.0.0/8", tree.cidr_map)
        node_10 = tree.cidr_map["10.0.0.0/8"]
        self.assertEqual(len(node_10.children), 2)
        
        child_cidrs = [child.cidr for child in node_10.children]
        self.assertIn("10.1.0.0/16", child_cidrs)
        self.assertIn("10.2.0.0/16", child_cidrs)
        
        node_10_1 = tree.cidr_map["10.1.0.0/16"]
        self.assertEqual(len(node_10_1.children), 1)
        self.assertEqual(node_10_1.children[0].cidr, "10.1.1.0/24")
    
    def test_duplicate_cidrs(self):
        """Test that duplicate CIDRs are handled correctly"""
        cidrs = [
            "10.0.0.0/8",
            "10.0.0.0/8",  # Duplicate
            "10.1.0.0/16",
            "10.1.0.0/16"   # Duplicate
        ]
        
        tree = CIDRTree()
        tree.build_tree_from_list(cidrs)
        
        # Should only have one instance of each CIDR
        self.assertEqual(len(tree.cidr_map), 2)
        self.assertIn("10.0.0.0/8", tree.cidr_map)
        self.assertIn("10.1.0.0/16", tree.cidr_map)
        
        # Verify parent-child relationship
        node_10 = tree.cidr_map["10.0.0.0/8"]
        self.assertEqual(len(node_10.children), 1)
        self.assertEqual(node_10.children[0].cidr, "10.1.0.0/16")
    
    def test_ipv6_cidrs(self):
        """Test with IPv6 CIDRs"""
        cidrs = [
            "2001:db8::/32",
            "2001:db8:1::/48",
            "2001:db8:1:1::/64"
        ]
        
        tree = CIDRTree()
        tree.build_tree_from_list(cidrs)
        
        # Verify the tree structure
        self.assertIn("2001:db8::/32", tree.cidr_map)
        node_root = tree.cidr_map["2001:db8::/32"]
        self.assertEqual(len(node_root.children), 1)
        
        node_48 = node_root.children[0]
        self.assertEqual(node_48.cidr, "2001:db8:1::/48")
        self.assertEqual(len(node_48.children), 1)
        self.assertEqual(node_48.children[0].cidr, "2001:db8:1:1::/64")

def run_tests():
    """Run the tests and print results"""
    print("Running tests for build_tree_from_list...")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    print("\nAll tests completed!")

if __name__ == "__main__":
    run_tests()
