import os
import sys

# Ensure "api/" is on sys.path so "import src.*" works in CI and locally
_API_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _API_DIR not in sys.path:
    sys.path.insert(0, _API_DIR)
