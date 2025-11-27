#!/usr/bin/env python3
"""
Script to combine all case files into a single JSON file.

This script:
1. Reads all case_*.json files from datasets/loan_arbitration/raw/
2. Combines all questions and answers into one unified JSON file
3. Preserves the structure and context information
"""

import json
from pathlib import Path
from typing import List, Dict, Any


def combine_all_cases(raw_dir: Path, output_file: Path):
    """
    Combine all case files into a single JSON file.
    
    Args:
        raw_dir: Path to the raw directory containing case files
        output_file: Path to the output combined JSON file
    """
    # Get all case files
    case_files = sorted(raw_dir.glob("case_*.json"))
    
    if not case_files:
        print(f"No case_*.json files found in {raw_dir}")
        return
    
    print(f"Found {len(case_files)} case files to combine...\n")
    
    # List to store all combined data
    all_questions = []
    total_questions = 0
    processed_files = 0
    skipped_files = 0
    
    # Process each file
    for case_file in case_files:
        try:
            print(f"Processing {case_file.name}...", end=" ")
            
            # Read the JSON file
            with open(case_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if data is a list
            if not isinstance(data, list):
                print(f"[SKIP] Not a list format")
                skipped_files += 1
                continue
            
            # Add all questions from this file
            questions_in_file = 0
            for item in data:
                if isinstance(item, dict) and 'question' in item:
                    all_questions.append(item)
                    questions_in_file += 1
            
            total_questions += questions_in_file
            processed_files += 1
            print(f"[OK] Added {questions_in_file} questions")
            
        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid JSON: {e}")
            skipped_files += 1
        except Exception as e:
            print(f"[ERROR] Error processing: {e}")
            skipped_files += 1
    
    # Write combined data to output file
    print(f"\nWriting combined data to {output_file}...")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_questions, f, ensure_ascii=False, indent=2)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Combination Summary:")
    print(f"  Files processed: {processed_files}/{len(case_files)}")
    print(f"  Files skipped:   {skipped_files}")
    print(f"  Total questions:  {total_questions}")
    print(f"  Output file:      {output_file}")
    print(f"  File size:        {output_file.stat().st_size / 1024 / 1024:.2f} MB")
    print(f"{'='*60}")


def main():
    """Main function."""
    # Define paths
    raw_dir = Path("datasets/loan_arbitration/raw")
    output_file = Path("datasets/loan_arbitration/combined_cases.json")
    
    if not raw_dir.exists():
        print(f"Error: Directory {raw_dir} does not exist!")
        return
    
    print("="*60)
    print("Combining All Case Files into Single JSON File")
    print("="*60)
    print()
    
    # Combine all cases
    combine_all_cases(raw_dir, output_file)
    
    print(f"\nSuccessfully created combined file: {output_file}")


if __name__ == "__main__":
    main()

