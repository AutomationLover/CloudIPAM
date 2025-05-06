# IPAM and CIDR Tree Implementation

A Python implementation of IP Address Management (IPAM) with CIDR tree structure for efficient IP address management and hierarchy representation.

## Project Structure

```
.
├── src/                    # Source code
│   ├── aws_provider.py     # AWS cloud provider implementation
│   ├── cidrtree.py         # CIDR tree implementation
│   └── ipam.py             # IPAM core functionality
├── test/
│   └── unittest/         # Unit tests
│       ├── data/           # Test data files
│       │   ├── cloud_cidrs.json
│       │   ├── static_cidrs.json
│       │   └── test_cidrs.json
│       ├── test_build_tree.py
│       ├── test_cidrtree.py
│       ├── test_ipam.py
│       ├── test_ipam_updated.py
│       └── test_ipam_with_data.py
├── CHANGELOG.md
└── README.md
```

## Running Unit Tests

### Prerequisites
- Python 3.7 or higher
- Virtual environment (recommended)

### Setting Up the Development Environment

1. **Create and activate a virtual environment**:
   ```bash
   # Create a virtual environment
   python -m venv venv
   
   # Activate the virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   # .\venv\Scripts\activate
   ```

2. **Install required packages**:
   ```bash
   # Install core requirements
   pip install -r requirements.txt
   
   # Additional development dependencies
   pip install boto3  # Required for AWS provider tests
   ```

### Running Tests

#### Running All Tests

To run all tests in the test suite:

```bash
# Navigate to the tests directory
cd test/unittest

# Run all tests with verbosity
python -m unittest discover -v
```

#### Running Specific Test Files

To run all tests in a specific file (e.g., `test_ipam_with_data.py`):

```bash
cd test/unittest
python -m unittest test_ipam_with_data.py -v
```

#### Running Individual Test Cases

To run a specific test case (e.g., `TestBuildTreeFromList`):

```bash
cd test/unittest
python -m unittest test_build_tree.TestBuildTreeFromList -v
```

To run a specific test method within a test case:

```bash
cd test/unittest
python -m unittest test_build_tree.TestBuildTreeFromList.test_specific_method -v
```

## Using Local JSON Files for Testing

Test data is stored in the `test/unittest/data/` directory. The following JSON files are used:

1. **test_cidrs.json**: Sample CIDR data for basic testing
2. **static_cidrs.json**: Static CIDR definitions
3. **cloud_cidrs.json**: Cloud provider CIDR data

### Example: Using JSON Files in Tests

```python
# Example from test_ipam_with_data.py
with open('data/static_cidrs.json', 'w') as f:
    json.dump(test_data, f)

# Then in your test method
ipam.load_static_cidrs('data/static_cidrs.json')
```

### Creating Custom Test Data

1. Create a new JSON file in the `test/unittest/data/` directory
2. Define your test data following the existing format
3. Update the test methods to use your custom data file

## Test Coverage

The test suite includes comprehensive coverage for:
- Basic CIDR tree construction
- Multi-level hierarchy
- Non-contiguous CIDR blocks
- Mixed IPv4 and IPv6 environments
- Parent-child relationships
- Tag management
- Cloud provider integration

## Troubleshooting

If you encounter import errors:
1. Ensure you're running tests from the `test/unittest` directory
2. Verify the Python path includes the project root
3. Check that all required packages are installed in your virtual environment
