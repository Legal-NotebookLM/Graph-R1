#!/usr/bin/env python3
"""
Script to split raw case files into train/val/test folders for fine-tuning.

This script:
1. Reads all case_*.json files from datasets/loan_arbitration/raw/
2. Splits them into train (70%), val (15%), and test (15%) folders
3. Moves files to respective folders for fine-tuning tasks
"""

import json
import shutil
from pathlib import Path
from typing import List
import random


def split_files_into_folders(
    raw_dir: Path,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15
):
    """
    Split case files into train/val/test folders.
    
    Args:
        raw_dir: Path to the raw directory containing case files
        train_ratio: Proportion of files for training (default: 0.70)
        val_ratio: Proportion of files for validation (default: 0.15)
        test_ratio: Proportion of files for testing (default: 0.15)
    """
    # Validate ratios
    if abs(train_ratio + val_ratio + test_ratio - 1.0) > 0.001:
        raise ValueError("Ratios must sum to 1.0")
    
    # Get all case files
    case_files = sorted(raw_dir.glob("case_*.json"))
    
    if not case_files:
        print(f"No case_*.json files found in {raw_dir}")
        return
    
    print(f"Found {len(case_files)} case files to split...\n")
    
    # Shuffle files for random distribution
    random.seed(42)  # For reproducibility
    shuffled_files = case_files.copy()
    random.shuffle(shuffled_files)
    
    # Calculate split indices
    total_files = len(shuffled_files)
    train_end = int(total_files * train_ratio)
    val_end = train_end + int(total_files * val_ratio)
    
    # Split files
    train_files = shuffled_files[:train_end]
    val_files = shuffled_files[train_end:val_end]
    test_files = shuffled_files[val_end:]
    
    print(f"Split distribution:")
    print(f"  Train: {len(train_files)} files ({len(train_files)/total_files*100:.1f}%)")
    print(f"  Val:   {len(val_files)} files ({len(val_files)/total_files*100:.1f}%)")
    print(f"  Test:  {len(test_files)} files ({len(test_files)/total_files*100:.1f}%)")
    print()
    
    # Create output directories
    base_dir = raw_dir.parent
    train_dir = base_dir / "train"
    val_dir = base_dir / "val"
    test_dir = base_dir / "test"
    
    for folder in [train_dir, val_dir, test_dir]:
        folder.mkdir(exist_ok=True)
        print(f"Created/verified directory: {folder}")
    
    print()
    
    # Move files to respective folders
    def move_files(files: List[Path], target_dir: Path, split_name: str):
        """Move files to target directory."""
        moved_count = 0
        for file_path in files:
            try:
                target_path = target_dir / file_path.name
                shutil.copy2(file_path, target_path)  # Copy instead of move to keep originals
                moved_count += 1
                print(f"  [OK] Copied {file_path.name} -> {target_dir.name}/")
            except Exception as e:
                print(f"  [ERROR] Failed to copy {file_path.name}: {e}")
        return moved_count
    
    # Move train files
    print(f"Copying {len(train_files)} files to train/...")
    train_count = move_files(train_files, train_dir, "train")
    
    # Move val files
    print(f"\nCopying {len(val_files)} files to val/...")
    val_count = move_files(val_files, val_dir, "val")
    
    # Move test files
    print(f"\nCopying {len(test_files)} files to test/...")
    test_count = move_files(test_files, test_dir, "test")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Split Summary:")
    print(f"  Train: {train_count}/{len(train_files)} files copied")
    print(f"  Val:   {val_count}/{len(val_files)} files copied")
    print(f"  Test:  {test_count}/{len(test_files)} files copied")
    print(f"  Total: {train_count + val_count + test_count}/{total_files} files")
    print(f"{'='*60}")
    
    # Print file lists for reference
    print(f"\nTrain files ({len(train_files)}):")
    for f in sorted(train_files):
        print(f"  - {f.name}")
    
    print(f"\nVal files ({len(val_files)}):")
    for f in sorted(val_files):
        print(f"  - {f.name}")
    
    print(f"\nTest files ({len(test_files)}):")
    for f in sorted(test_files):
        print(f"  - {f.name}")


def main():
    """Main function."""
    # Define paths
    raw_dir = Path("datasets/loan_arbitration/raw")
    
    if not raw_dir.exists():
        print(f"Error: Directory {raw_dir} does not exist!")
        return
    
    print("="*60)
    print("Splitting Raw Case Files into Train/Val/Test Folders")
    print("="*60)
    print()
    
    # Split files (70% train, 15% val, 15% test)
    split_files_into_folders(
        raw_dir,
        train_ratio=0.70,
        val_ratio=0.15,
        test_ratio=0.15
    )


if __name__ == "__main__":
    main()

