import sys
from pathlib import Path

# Add project root to sys.path so tests can import project modules
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
