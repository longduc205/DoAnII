#!/usr/bin/env python3
"""
Train Model Script

Convenience wrapper around ``ai.trainer`` for running inside Docker
or from the project root.

Usage:
    python scripts/train_model.py
    python scripts/train_model.py --data data/raw/combined_training_data.csv

    # Inside Docker:
    docker exec -it ai-vuln-scanner python scripts/train_model.py
"""

import os
import sys

# Ensure project root is on sys.path so `ai.*` imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.trainer import main  # noqa: E402

if __name__ == '__main__':
    main()
