#!/usr/bin/env python3
"""
Test IPAM with comprehensive test data from JSON files
"""
import json
import os
import sys
import tempfile
import unittest
import os
import json
import ipaddress
import sys

# Add the parent directory to the path so we can import the IPAM module
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.ipam import IPAM, CIDR, TestProvider

class TestIPAMSimpleData(unittest.TestCase):
    """Test IPAM with simple in-memory test data"""
    
    @classmethod
    def setUpClass(cls):
        print("\n" + "="*80)
        print(f"[SETUP] Starting {cls.__name__}.setUpClass()")
        print("="*80)
        
        # Initialize test data
        print("\n[SETUP] Initializing simple static test data...")
        cls.static_data = {
            "cidrs": [
                {
                    "cidr": "10.0.0.0/8",
                    "type": "NETWORK",
                    "tags": {"environment": "prod", "region": "global"}
                },
                {
                    "cidr": "10.1.0.0/16",
                    "type": "VPC",
                    "tags": {"environment": "prod", "region": "us-east-1"}
                }
            ]
        }
        print(f"[SETUP] Loaded {len(cls.static_data['cidrs'])} static CIDRs")
        
        # Initialize cloud test data in the format expected by TestProvider
        print("\n[SETUP] Initializing simple cloud test data...")
        cls.cloud_data = {
            "cidrs": [
                {
                    "cidr": "10.100.0.0/16",
                    "type": "VPC",
                    "tags": {
                        "Name": "test-vpc-1",
                        "Environment": "test"
                    }
                }
            ]
        }
        print(f"[SETUP] Loaded {len(cls.cloud_data['cidrs'])} cloud VPCs")
        
        # Initialize IPAM with test provider
        cls.ipam = IPAM()
        
        # Add test data directly to IPAM
        for cidr_data in cls.static_data["cidrs"]:
            cidr = CIDR(
                cidr=cidr_data['cidr'],
                cidr_type=cidr_data['type'],
                tags=cidr_data.get('tags', {})
            )
            if not hasattr(cls.ipam, 'cidrs'):
                cls.ipam.cidrs = {}
            cls.ipam.cidrs[cidr_data['cidr']] = cidr
            
        print("[SETUP] Added test data to IPAM instance")

    def test_static_provider_hierarchy(self):
        """Test hierarchy building with static provider data"""
        # Use the pre-initialized IPAM instance with static data
        ipam = self.ipam
        
        # Verify we loaded the expected number of CIDRs
        self.assertEqual(len(ipam.cidrs), len(self.static_data['cidrs']))
        
        # Verify specific CIDRs exist with correct data
        for cidr_data in self.static_data['cidrs']:
            cidr = cidr_data['cidr']
            self.assertIn(cidr, ipam.cidrs)
            self.assertEqual(ipam.cidrs[cidr].cidr_type, cidr_data['type'])
            self.assertEqual(ipam.cidrs[cidr].tags, cidr_data['tags'])
        
        # Test hierarchy building
        cidr_objects = list(ipam.cidrs.values())
        if cidr_objects:
            CIDR.build_hierarchy(cidr_objects)

    def test_cloud_provider_hierarchy(self):
        """Test loading cloud data using TestProvider with in-memory data"""
        # Create a temporary file with the cloud data
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as temp_file:
            json.dump(self.cloud_data, temp_file)
            temp_file_path = temp_file.name
        
        try:
            # Create IPAM with test provider
            test_provider = TestProvider(temp_file_path)
            ipam = IPAM(cloud_provider=test_provider)
            
            # Load cloud CIDRs through the provider
            ipam.load_cloud_cidrs()
            
            # Build the hierarchy
            ipam.build_hierarchy()
            
            # Verify we loaded the expected number of cloud CIDRs
            self.assertEqual(len(ipam.cidrs), len(self.cloud_data['cidrs']))
            
            # Verify each cloud CIDR exists with correct data
            for cidr_data in self.cloud_data['cidrs']:
                cidr = cidr_data['cidr']
                self.assertIn(cidr, ipam.cidrs)
                self.assertEqual(ipam.cidrs[cidr].cidr_type, 'VPC')
                for tag_key, tag_value in cidr_data['tags'].items():
                    self.assertEqual(ipam.cidrs[cidr].tags.get(tag_key), tag_value)
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    def test_combined_providers(self):
        """Test combining static and cloud providers"""
        # Create IPAM with test provider
        ipam = IPAM()
        
        # Add static data directly
        for cidr_data in self.static_data["cidrs"]:
            cidr = CIDR(
                cidr=cidr_data['cidr'],
                cidr_type=cidr_data['type'],
                tags=cidr_data.get('tags', {})
            )
            ipam.cidrs[cidr_data['cidr']] = cidr
        
        # Add cloud data directly using the new format
        for cidr_data in self.cloud_data['cidrs']:
            cidr = CIDR(
                cidr=cidr_data['cidr'],
                cidr_type=cidr_data['type'],
                tags=cidr_data.get('tags', {})
            )
            ipam.cidrs[cidr_data['cidr']] = cidr
        
        # Verify we have CIDRs from both sources
        expected_total = len(self.static_data['cidrs']) + len(self.cloud_data['cidrs'])
        self.assertEqual(len(ipam.cidrs), expected_total)
        
        # Verify specific CIDRs from both sources exist
        self.assertIn('10.0.0.0/8', ipam.cidrs)      # From static
        self.assertIn('10.1.0.0/16', ipam.cidrs)     # From static
        self.assertIn('10.100.0.0/16', ipam.cidrs)   # From cloud


class TestIPAMWithJsonData(unittest.TestCase):
    """Test IPAM with data loaded from JSON files in test/unittest/data"""
    
    @classmethod
    def setUpClass(cls):
        print("\n" + "="*80)
        print(f"[SETUP] Starting {cls.__name__}.setUpClass()")
        print("="*80)
        
        # Set paths to the test data files
        test_data_dir = os.path.join(os.path.dirname(__file__), 'data')
        cls.static_file = os.path.join(test_data_dir, 'static_cidrs.json')
        cls.cloud_file = os.path.join(test_data_dir, 'cloud_cidrs.json')
        
        print(f"[SETUP] Using static CIDRs from: {cls.static_file}")
        print(f"[SETUP] Using cloud CIDRs from: {cls.cloud_file}")
        
        # Verify test data files exist
        if not os.path.exists(cls.static_file):
            raise FileNotFoundError(f"Static CIDRs file not found: {cls.static_file}")
        if not os.path.exists(cls.cloud_file):
            raise FileNotFoundError(f"Cloud CIDRs file not found: {cls.cloud_file}")
        
        # Load the test data to verify it's valid JSON
        with open(cls.static_file, 'r') as f:
            static_data = json.load(f)
            print(f"[SETUP] Loaded {len(static_data.get('cidrs', []))} static CIDRs")
            
        with open(cls.cloud_file, 'r') as f:
            cloud_data = json.load(f)
            print(f"[SETUP] Loaded {len(cloud_data.get('cidrs', []))} cloud CIDRs")
    
    def test_static_provider_hierarchy(self):
        """Test hierarchy building with static provider data from JSON file"""
        # Create IPAM and load from JSON file
        ipam = IPAM()
        ipam.load_static_cidrs(self.static_file)
        
        # Expected CIDRs from the static file
        # Note: The actual implementation uses 'STATIC' as the type for all static CIDRs
        expected_cidrs = {
            '10.0.0.0/8': {'type': 'STATIC', 'env': 'prod', 'region': 'global'},
            '10.1.0.0/16': {'type': 'STATIC', 'env': 'prod', 'region': 'us-east-1'},
            '10.2.0.0/16': {'type': 'STATIC', 'env': 'dev', 'region': 'us-west-2'}
        }
        
        # Verify we loaded the expected number of CIDRs
        self.assertEqual(len(ipam.cidrs), len(expected_cidrs))
        
        # Verify each CIDR exists with correct data
        for cidr, expected in expected_cidrs.items():
            self.assertIn(cidr, ipam.cidrs)
            self.assertEqual(ipam.cidrs[cidr].cidr_type, expected['type'])
            self.assertEqual(ipam.cidrs[cidr].tags.get('environment'), expected['env'])
            self.assertEqual(ipam.cidrs[cidr].tags.get('region'), expected['region'])
        
        # Test hierarchy building
        cidr_objects = list(ipam.cidrs.values())
        if cidr_objects:
            CIDR.build_hierarchy(cidr_objects)
    
    def test_cloud_provider_hierarchy(self):
        """Test loading cloud data from JSON file"""
        # Create IPAM with test provider
        ipam = IPAM(cloud_provider=TestProvider(self.cloud_file))
        ipam.load_cloud_cidrs()
        
        # Expected cloud CIDRs from the cloud file
        expected_cloud_cidrs = {
            '10.100.0.0/16': {'name': 'test-vpc-1', 'env': 'test'},
            '10.200.0.0/16': {'name': 'test-vpc-2', 'env': 'staging'}
        }
        
        # Verify we loaded the expected number of cloud CIDRs
        self.assertEqual(len(ipam.cidrs), len(expected_cloud_cidrs))
        
        # Verify each cloud CIDR exists with correct data
        for cidr, expected in expected_cloud_cidrs.items():
            self.assertIn(cidr, ipam.cidrs)
            self.assertEqual(ipam.cidrs[cidr].tags.get('Name'), expected['name'])
            self.assertEqual(ipam.cidrs[cidr].tags.get('Environment'), expected['env'])
    
    def test_combined_providers(self):
        """Test combining static and cloud providers with JSON data"""
        # Create IPAM with test provider
        test_provider = TestProvider(self.cloud_file)
        ipam = IPAM(cloud_provider=test_provider)
        
        # Load both static and cloud data
        ipam.load_static_cidrs(self.static_file)
        ipam.load_cloud_cidrs()
        
        # Load the test data to get expected counts
        with open(self.static_file, 'r') as f:
            static_data = json.load(f)
        with open(self.cloud_file, 'r') as f:
            cloud_data = json.load(f)
            
        expected_static_count = len(static_data.get('cidrs', []))
        expected_cloud_count = len(cloud_data.get('cidrs', []))
        
        # Verify we have CIDRs from both sources
        self.assertEqual(len(ipam.cidrs), expected_static_count + expected_cloud_count)
        
        # Verify specific CIDRs from both sources exist
        for cidr_data in static_data.get('cidrs', []):
            self.assertIn(cidr_data['cidr'], ipam.cidrs)
            
        for cidr_data in cloud_data.get('cidrs', []):
            self.assertIn(cidr_data['cidr'], ipam.cidrs)

if __name__ == '__main__':
    unittest.main()
