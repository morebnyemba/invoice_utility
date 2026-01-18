#!/usr/bin/env python3
"""
API Server Entry Point
"""
import sys
import os

# Add the parent directory to the path so we can import from src
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.api.api import app

if __name__ == '__main__':
    # Run the Flask app
    port = int(os.getenv('API_PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    print(f"Starting Invoice Utility API Server on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=debug)
