"""
DevRecall Entrypoint.
Usage:
    python main.py demo
    python main.py query "how to start postgres"
    python main.py retain "Local docker postgres port is 5433"
    python main.py list
"""

import sys
from devrecall.cli import run_interactive

if __name__ == "__main__":
    run_interactive(sys.argv[1:])
