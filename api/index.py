import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Now import the app
from src.main import app

# Vercel handler
handler = app
