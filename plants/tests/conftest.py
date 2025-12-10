# Import fixtures from root tests/conftest.py so they're available to this directory
import sys
from pathlib import Path

# Add parent directory to path so we can import from tests
root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root))

# Re-export all fixtures from tests/conftest.py
from tests.conftest import *
