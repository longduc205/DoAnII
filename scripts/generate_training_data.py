#!/usr/bin/env python3
"""
Training Data Generator

Generates synthetic labeled HTTP response samples for ML model training.
Creates realistic normal and suspicious response features without requiring
a live vulnerable target.

Usage:
    python scripts/generate_training_data.py
    python scripts/generate_training_data.py --normal 200 --suspicious 200
    python scripts/generate_training_data.py --seed 123 --output data/custom.csv
"""

import sys


def main():
    """Main entry point."""
    print("[DataGenerator] Starting...")


if __name__ == '__main__':
    main()
