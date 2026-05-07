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

import argparse
import sys


def parse_arguments():
    """Parse command-line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments with attributes:
            - normal (int): Number of normal samples
            - suspicious (int): Number of suspicious samples
            - seed (int): Random seed for reproducibility
            - output (str): Output CSV file path
    """
    parser = argparse.ArgumentParser(
        description='Generate synthetic training data for vulnerability classification',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate default 500+500 samples
  python scripts/generate_training_data.py
  
  # Generate custom sample counts
  python scripts/generate_training_data.py --normal 200 --suspicious 200
  
  # Use custom seed and output path
  python scripts/generate_training_data.py --seed 123 --output data/train.csv
        """
    )
    
    parser.add_argument(
        '--normal',
        type=int,
        default=500,
        help='Number of normal (non-vulnerable) samples to generate (default: 500)'
    )
    
    parser.add_argument(
        '--suspicious',
        type=int,
        default=500,
        help='Number of suspicious (vulnerable) samples to generate (default: 500)'
    )
    
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Random seed for reproducibility (default: 42)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='data/raw/training_data.csv',
        help='Output CSV file path (default: data/raw/training_data.csv)'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.normal <= 0:
        parser.error('--normal must be a positive integer')
    if args.suspicious <= 0:
        parser.error('--suspicious must be a positive integer')
    if args.seed < 0:
        parser.error('--seed must be a non-negative integer')
    
    return args


def main():
    """Main entry point."""
    args = parse_arguments()
    
    print(f"[DataGenerator] Configuration:")
    print(f"  Normal samples: {args.normal}")
    print(f"  Suspicious samples: {args.suspicious}")
    print(f"  Random seed: {args.seed}")
    print(f"  Output path: {args.output}")


if __name__ == '__main__':
    main()
