#!/usr/bin/env python3
"""
Script to split combined_cases.json into qa_train.json, qa_dev.json, and qa_test.json.

This script:
1. Reads the combined_cases.json file
2. Splits it into train (70%), dev (15%), and test (15%) sets
3. Saves them as qa_train.json, qa_dev.json, qa_test.json in the raw folder
"""

import json
import random
from pathlib import Path
from typing import List, Dict, Any


def split_combined_data(
    input_file: Path,
    output_dir: Path,
    train_ratio: float = 0.70,
    dev_ratio: float = 0.15,
    test_ratio: float = 0.15,
    seed: int = 42
):
    """
    Split combined data into train/dev/test sets.
    
    Args:
        input_file: Path to the combined JSON file
        output_dir: Directory to save the split files
        train_ratio: Proportion for training (default: 0.70)
        dev_ratio: Proportion for development (default: 0.15)
        test_ratio: Proportion for testing (default: 0.15)
        seed: Random seed for reproducibility
    """
    # Validate ratios
    if abs(train_ratio + dev_ratio + test_ratio - 1.0) > 0.001:
        raise ValueError("Ratios must sum to 1.0")
    
    # Read combined data
    print(f"Reading combined data from {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        all_data = json.load(f)
    
    if not isinstance(all_data, list):
        raise ValueError("Input file must contain a JSON array")
    
    total_items = len(all_data)
    print(f"Total questions: {total_items}\n")
    
    # Shuffle data for random distribution
    random.seed(seed)
    shuffled_data = all_data.copy()
    random.shuffle(shuffled_data)
    
    # Calculate split indices
    train_end = int(total_items * train_ratio)
    dev_end = train_end + int(total_items * dev_ratio)
    
    # Split data
    train_data = shuffled_data[:train_end]
    dev_data = shuffled_data[train_end:dev_end]
    test_data = shuffled_data[dev_end:]
    
    print(f"Split distribution:")
    print(f"  Train: {len(train_data)} questions ({len(train_data)/total_items*100:.1f}%)")
    print(f"  Dev:   {len(dev_data)} questions ({len(dev_data)/total_items*100:.1f}%)")
    print(f"  Test:  {len(test_data)} questions ({len(test_data)/total_items*100:.1f}%)")
    print()
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save split files
    def save_json(data: List[Dict], filename: str):
        """Save data to JSON file."""
        filepath = output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        file_size = filepath.stat().st_size / 1024  # KB
        print(f"  [OK] Saved {filename} ({len(data)} questions, {file_size:.2f} KB)")
    
    print("Saving split files...")
    save_json(train_data, "qa_train.json")
    save_json(dev_data, "qa_dev.json")
    save_json(test_data, "qa_test.json")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Split Summary:")
    print(f"  Input file:  {input_file}")
    print(f"  Output dir:  {output_dir}")
    print(f"  Train:       {len(train_data)} questions -> qa_train.json")
    print(f"  Dev:         {len(dev_data)} questions -> qa_dev.json")
    print(f"  Test:        {len(test_data)} questions -> qa_test.json")
    print(f"  Total:       {total_items} questions")
    print(f"{'='*60}")


def main():
    """Main function."""
    # Define paths
    input_file = Path("datasets/loan_arbitration/combined_cases.json")
    output_dir = Path("datasets/loan_arbitration/raw")
    
    if not input_file.exists():
        print(f"Error: Input file {input_file} does not exist!")
        print("Please run combine_cases.py first to create the combined file.")
        return
    
    print("="*60)
    print("Splitting Combined Data into Train/Dev/Test Sets")
    print("="*60)
    print()
    
    # Split data (70% train, 15% dev, 15% test)
    split_combined_data(
        input_file,
        output_dir,
        train_ratio=0.70,
        dev_ratio=0.15,
        test_ratio=0.15,
        seed=42
    )
    
    print("\nSuccessfully created qa_train.json, qa_dev.json, and qa_test.json")


if __name__ == "__main__":
    main()

