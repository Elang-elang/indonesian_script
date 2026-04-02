#!/usr/bin/env python3
"""
Entry point untuk menjalankan module sebagai script:
python -m indonesian_script <filename>
"""

import sys
from .Cli.main import main

if __name__ == "__main__":
    sys.exit(main())