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
import os
import sys

# Add project root to path so we can import ai modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.data_collector import TrainingDataCollector


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


def generate_data(n_normal, n_suspicious, seed, output_path):
    """Generate synthetic training data and save to CSV.
    
    Args:
        n_normal (int): Number of normal samples
        n_suspicious (int): Number of suspicious samples
        seed (int): Random seed
        output_path (str): Output CSV file path
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print(f"[DataGenerator] Starting synthetic data generation...")
        
        # Initialize collector
        collector = TrainingDataCollector()
        
        # Generate samples
        print(f"[DataGenerator] Generating {n_normal} normal samples...")
        print(f"[DataGenerator] Generating {n_suspicious} suspicious samples...")
        collector.generate_synthetic(
            n_normal=n_normal,
            n_suspicious=n_suspicious,
            seed=seed
        )
        
        # Get sample counts for verification
        n_normal_actual, n_suspicious_actual = collector.get_sample_count()
        
        # Save to CSV
        print(f"[DataGenerator] Saving to {output_path}...")
        collector.save_to_csv(output_path)
        
        # Get file size
        file_size_bytes = os.path.getsize(output_path)
        file_size_kb = file_size_bytes / 1024
        
        # Print success summary
        print(f"[DataGenerator] ✓ Success!\n")
        print(f"Summary:")
        print(f"  Total samples: {n_normal_actual + n_suspicious_actual}")
        print(f"  Normal (label=0): {n_normal_actual} ({n_normal_actual/(n_normal_actual+n_suspicious_actual)*100:.1f}%)")
        print(f"  Suspicious (label=1): {n_suspicious_actual} ({n_suspicious_actual/(n_normal_actual+n_suspicious_actual)*100:.1f}%)")
        print(f"  Output file: {output_path}")
        print(f"  File size: ~{file_size_kb:.1f} KB")
        
        return True
        
    except ImportError as e:
        print(f"[ERROR] Cannot import required modules: {e}", file=sys.stderr)
        print(f"        Make sure you're running this script from the project root directory.", file=sys.stderr)
        return False
        
    except OSError as e:
        print(f"[ERROR] Cannot write to {output_path}", file=sys.stderr)
        print(f"        {e}", file=sys.stderr)
        return False
        
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}", file=sys.stderr)
        return False


def main():
    """Main entry point."""
    args = parse_arguments()
    
    # Generate data
    success = generate_data(
        n_normal=args.normal,
        n_suspicious=args.suspicious,
        seed=args.seed,
        output_path=args.output
    )
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
