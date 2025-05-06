import os
import sys
import unittest

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.ipam import IPAM, TestProvider, CIDR
import tempfile
import json

class TestIPAM(unittest.TestCase):
    def setUp(self):
        # Create a temporary test file
        self.test_file = tempfile.NamedTemporaryFile(delete=False)
        test_data = {
            "cidrs": [
                {
                    "cidr": "10.0.0.0/8",
                    "type": "VPC",
                    "tags": {
                        "environment": "prod",
                        "purpose": "base"
                    }
                },
                {
                    "cidr": "10.1.0.0/16",
                    "type": "SUBNET",
                    "tags": {
                        "environment": "prod",
                        "purpose": "web"
                    }
                },
                {
                    "cidr": "10.2.0.0/16",
                    "type": "SUBNET",
                    "tags": {
                        "environment": "prod",
                        "purpose": "db"
                    }
                }
            ]
        }
        with open(self.test_file.name, 'w') as f:
            json.dump(test_data, f)

        # Create IPAM instance with test provider
        self.provider = TestProvider(self.test_file.name)
        self.ipam = IPAM(cloud_provider=self.provider)

    def tearDown(self):
        # Clean up temporary file
        self.test_file.close()
        import os
        os.unlink(self.test_file.name)

    def test_load_cidrs(self):
        """Test loading CIDRs from both static file and cloud provider"""
        # Create temporary static CIDRs file
        with tempfile.NamedTemporaryFile(delete=False, mode='w') as static_file:
            static_data = {
                "cidrs": [
                    {
                        "cidr": "192.168.0.0/16",
                        "tags": {
                            "environment": "dev",
                            "purpose": "test"
                        }
                    }
                ]
            }
            json.dump(static_data, static_file)

        # Load static CIDRs
        self.ipam.load_static_cidrs(static_file.name)
        # Load cloud CIDRs
        self.ipam.load_cloud_cidrs()

        # Verify CIDRs are loaded
        self.assertIn("10.0.0.0/8", self.ipam.cidrs)
        self.assertIn("192.168.0.0/16", self.ipam.cidrs)

        # Clean up
        import os
        os.unlink(static_file.name)

    def test_get_cidr_tags(self):
        """Test getting tags for a specific CIDR"""
        self.ipam.load_cloud_cidrs()
        
        # Get tags for VPC
        vpc_tags = self.ipam.get_cidr_tags("10.0.0.0/8")
        self.assertEqual(vpc_tags["environment"], "prod")
        self.assertEqual(vpc_tags["purpose"], "base")

        # Get tags for Subnet
        subnet_tags = self.ipam.get_cidr_tags("10.1.0.0/16")
        self.assertEqual(subnet_tags["environment"], "prod")
        self.assertEqual(subnet_tags["purpose"], "web")

    def test_find_cidrs_by_tag(self):
        """Test finding CIDRs by tags"""
        self.ipam.load_cloud_cidrs()
        
        # Find by environment tag
        prod_cidrs = self.ipam.find_cidrs_by_tag("environment", "prod")
        self.assertEqual(len(prod_cidrs), 3)
        
        # Find by purpose tag
        web_cidrs = self.ipam.find_cidrs_by_tag("purpose", "web")
        self.assertEqual(len(web_cidrs), 1)
        self.assertEqual(str(web_cidrs[0].cidr), "10.1.0.0/16")

    def test_get_child_cidrs(self):
        """Test getting direct child CIDRs"""
        self.ipam.load_cloud_cidrs()
        
        # Get child CIDRs of VPC
        children = self.ipam.get_child_cidrs("10.0.0.0/8")
        print(f"Found {len(children)} children:")
        for child in children:
            print(f"- {child.cidr} (parent: {child.parent.cidr if child.parent else 'None'})")
        
        self.assertEqual(len(children), 2)  # Only direct children
        child_cidrs = [str(c.cidr) for c in children]
        self.assertIn("10.1.0.0/16", child_cidrs)
        self.assertIn("10.2.0.0/16", child_cidrs)
        self.assertNotIn("10.0.0.0/8", child_cidrs)  # VPC is not its own child

        # Test with non-existent CIDR
        non_existent = self.ipam.get_child_cidrs("10.0.0.0/24")
        self.assertEqual(len(non_existent), 0)

    def test_find_available_cidr(self):
        """Test finding available CIDRs"""
        self.ipam.load_cloud_cidrs()
        
        # Find available /24 in VPC
        available = self.ipam.find_available_cidr("10.0.0.0/8", 24)
        self.assertIsNotNone(available)
        self.assertEqual(available.cidr_type, "STATIC")
        self.assertEqual(available.tags["status"], "available")

        # Find available /24 in Subnet (should find one since we only have /16)
        subnet_available = self.ipam.find_available_cidr("10.1.0.0/16", 24)
        self.assertIsNotNone(subnet_available)
        self.assertEqual(subnet_available.cidr_type, "STATIC")
        self.assertEqual(subnet_available.tags["status"], "available")

if __name__ == '__main__':
    unittest.main()
