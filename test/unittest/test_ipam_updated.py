#!/usr/bin/env python3
"""
Test script for the updated IPAM implementation using CIDRTree
"""
import os
import sys
import unittest

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.ipam import CIDR

class TestCIDRWithTree(unittest.TestCase):
    def setUp(self):
        # Create test CIDRs
        self.cidr1 = CIDR("10.0.0.0/8", "network")
        self.cidr2 = CIDR("10.1.0.0/16", "subnet")
        self.cidr3 = CIDR("10.1.1.0/24", "subnet")
        self.cidr4 = CIDR("192.168.1.0/24", "network")
        
        # Build the hierarchy
        CIDR.build_hierarchy([self.cidr1, self.cidr2, self.cidr3, self.cidr4])
    
    def test_parent_child_relationships(self):
        """Test parent-child relationships"""
        # Check parent relationships
        self.assertIsNone(self.cidr1.parent)
        self.assertEqual(self.cidr2.parent, self.cidr1)
        self.assertEqual(self.cidr3.parent, self.cidr2)
        self.assertIsNone(self.cidr4.parent)
        
        # Check children relationships
        self.assertEqual(len(self.cidr1.children), 1)
        self.assertEqual(self.cidr1.children[0], self.cidr2)
        
        self.assertEqual(len(self.cidr2.children), 1)
        self.assertEqual(self.cidr2.children[0], self.cidr3)
        
        self.assertEqual(len(self.cidr3.children), 0)
        self.assertEqual(len(self.cidr4.children), 0)
    
    def test_hierarchy_methods(self):
        """Test hierarchy-related methods"""
        self.assertTrue(self.cidr1.is_parent_of(self.cidr2))
        self.assertTrue(self.cidr2.is_parent_of(self.cidr3))
        self.assertFalse(self.cidr1.is_parent_of(self.cidr4))
        
        self.assertTrue(self.cidr3.is_child_of(self.cidr2))
        self.assertTrue(self.cidr2.is_child_of(self.cidr1))
        self.assertFalse(self.cidr4.is_child_of(self.cidr1))
    
    def test_tags(self):
        """Test tag management"""
        self.cidr1.add_tag("environment", "prod")
        self.assertEqual(self.cidr1.get_tags(), {"environment": "prod"})
        
        self.cidr1.remove_tag("environment")
        self.assertEqual(self.cidr1.get_tags(), {})

def run_tests():
    """Run the tests and print results"""
    print("Running tests for updated IPAM with CIDRTree...")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    print("\nAll tests completed!")

if __name__ == "__main__":
    run_tests()
