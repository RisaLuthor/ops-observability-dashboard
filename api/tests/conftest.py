import os
import sys

# Add the api/ directory to sys.path so "import src.*" works in GitHub Actions.
API_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if API_DIR not in sys.path:
    sys.path.insert(0, API_DIR)
