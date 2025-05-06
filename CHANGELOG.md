# Changelog

All notable changes to the IPAM and CIDR Tree implementation will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-05-06

### Added
- Comprehensive test cases for multi-level CIDR hierarchies
- Support for testing non-contiguous CIDR blocks
- IPv4 and IPv6 mixed environment test cases
- Test coverage for complex parent-child relationships
- `src` directory for better code organization
- Improved test data management in `test/unittest/data`

### Changed
- Moved all Python source files to `src` directory
- Updated import statements to use new package structure
- Reorganized test directory structure
- Improved parent-child relationship handling in CIDR tree
- Enhanced test coverage and organization

### Fixed
- Fixed parent-child relationship tracking in CIDR tree
- Resolved import issues after directory reorganization
- Fixed test data paths in test files

## [0.1.0] - 2025-05-06

### Added
- Initial implementation of CIDR tree structure with `CIDRNode` and `CIDRTree` classes
- Support for building tree from a list of CIDRs with `build_tree` method
- Hierarchical tree visualization with `print_tree` method
- Support for both string and object-based CIDR representations
- Test cases demonstrating basic functionality

### Changed
- N/A

### Fixed
- N/A

## [0.2.0] - 2025-05-06

### Added (cidrtree.py)
- New `build_tree_from_list` method for optimized tree construction when all CIDRs are provided upfront
- Support for sorting CIDRs by prefix length and network address
- Enhanced test cases to demonstrate different tree building methods
- Improved error handling and input validation
- Added support for CIDR objects from IPAM system

### Changed (cidrtree.py)
- Refactored tree building logic for better performance
- Updated `build_tree` to use `build_tree_from_list` internally
- Improved tree visualization with proper indentation and tree-like structure

### Fixed (cidrtree.py)
- Fixed issue with duplicate nodes in the tree
- Fixed parent-child relationship detection
- Fixed handling of CIDRs with the same network but different prefix lengths

## [0.3.0] - 2025-05-06

### Added (ipam.py)
- Integrated CIDRTree for managing parent-child relationships in the CIDR class
- Added `build_hierarchy` class method to set up the tree structure
- Implemented `parent` and `children` properties that query the tree
- Added comprehensive test suite in `test_ipam_updated.py`
- Added proper string representation and equality comparison methods

### Changed (ipam.py)
- Replaced manual parent-child management with CIDRTree-based implementation
- Converted `parent` and `children` to properties
- Improved type hints and documentation
- Made the code more maintainable and efficient

### Fixed (ipam.py)
- Fixed potential issues with circular references in the old implementation
- Improved handling of edge cases in hierarchy management
