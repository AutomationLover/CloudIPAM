import unittest
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from cidrtree import CIDRTree

class TestCIDRTree(unittest.TestCase):
    def test_simple_tree(self):
        tree = CIDRTree()
        cidrs = ["10.0.0.0/8", "10.0.0.0/16", "10.0.0.0/20"]
        tree.formTreeFromCidrList(cidrs)
        expected = {
            "null": {
                "10.0.0.0/8": {
                    "10.0.0.0/16": {
                        "10.0.0.0/20": {}
                    }
                }
            }
        }
        result = json.loads(tree.getCidrTree(None))
        self.assertEqual(result, expected)

    def test_complex_ipv4(self):
        # Deep parent/child with many siblings, some with different mask lengths
        cidrs = [
            "10.0.0.0/8",  # root
            "10.1.0.0/16", "10.2.0.0/16", "10.3.0.0/16", "10.4.0.0/16", "10.5.0.0/16", "10.6.0.0/16", "10.7.0.0/16", "10.8.0.0/16", "10.9.0.0/16", "10.10.0.0/16",  # 10 siblings under /8
            "10.1.1.0/24", "10.1.2.0/24",  # children under 10.1.0.0/16
            "10.1.1.128/25",  # child under 10.1.1.0/24
            "10.1.1.192/26",  # child under 10.1.1.128/25 (deeper)
            "10.1.1.200/29",  # child under 10.1.1.192/26 (deepest)
            "10.2.1.0/24",  # another branch
            "10.2.1.128/25", "10.2.1.192/26", "10.2.1.200/29"  # deep branch for another sibling
        ]
        tree = CIDRTree()
        tree.formTreeFromCidrList(cidrs)
        cidr_tree_json = tree.getCidrTree(None)
        expected = {
            "null": {
                "10.0.0.0/8": {
                    "10.1.0.0/16": {
                        "10.1.1.0/24": {
                            "10.1.1.128/25": {
                                "10.1.1.192/26": {
                                    "10.1.1.200/29": {}
                                }
                            }
                        },
                        "10.1.2.0/24": {}
                    },
                    "10.2.0.0/16": {
                        "10.2.1.0/24": {
                            "10.2.1.128/25": {
                                "10.2.1.192/26": {
                                    "10.2.1.200/29": {}
                                }
                            }
                        }
                    },
                    "10.3.0.0/16": {},
                    "10.4.0.0/16": {},
                    "10.5.0.0/16": {},
                    "10.6.0.0/16": {},
                    "10.7.0.0/16": {},
                    "10.8.0.0/16": {},
                    "10.9.0.0/16": {},
                    "10.10.0.0/16": {}
                }
            }
        }
        self.assertEqual(json.loads(cidr_tree_json), expected)

    def test_various_cases(self):
        cases = [
            # Pure IPv4
            {
                "cidrs": ["192.168.0.0/16", "192.168.1.0/24", "192.168.1.128/25"],
                "expected": {
                    "null": {
                        "192.168.0.0/16": {
                            "192.168.1.0/24": {
                                "192.168.1.128/25": {}
                            }
                        }
                    }
                }
            },
            # Pure IPv6
            {
                "cidrs": ["2001:db8::/32", "2001:db8:1::/48", "2001:db8:1:1::/64"],
                "expected": {"null": {"2001:db8::/32": {"2001:db8:1::/48": {"2001:db8:1:1::/64": {}}}}}
            },
            # Mixed IPv4 and IPv6
            {
                "cidrs": ["10.0.0.0/8", "2001:db8::/32", "10.0.0.0/16", "2001:db8:1::/48"],
                "expected": {"null": {
                    "10.0.0.0/8": {"10.0.0.0/16": {}},
                    "2001:db8::/32": {"2001:db8:1::/48": {}}
                }}
            },
        ]
        for idx, case in enumerate(cases):
            with self.subTest(i=idx):
                tree = CIDRTree()
                tree.formTreeFromCidrList(case["cidrs"])
                result = json.loads(tree.getCidrTree(None))
                self.assertEqual(result, case["expected"])

if __name__ == "__main__":
    unittest.main()
