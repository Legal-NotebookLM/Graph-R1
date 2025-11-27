#!/usr/bin/env python3
"""
Script to add case ID and folder ID context to questions in JSON files.

This script processes all JSON files in the datasets/loan_arbitration/raw/ directory
and appends case ID and folder ID to the end of each question as context in the format:
<case_id:XXX, folder_id:ARB/2024/XXXX>
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any


def extract_case_number(filename: str) -> str:
    """Extract case number from filename (e.g., 'case_001.json' -> '001')."""
    match = re.search(r'case_(\d+)\.json', filename)
    if match:
        return match.group(1)
    return ""


def generate_folder_id(case_number: str) -> str:
    """Generate folder ID from case number (e.g., '001' -> 'ARB/2024/1001')."""
    try:
        case_num = int(case_number)
        folder_num = 1000 + case_num
        return f"ARB/2024/{folder_num}"
    except ValueError:
        return f"ARB/2024/1000"


def add_context_to_question(question: str, case_id: str, folder_id: str) -> str:
    """Add context to the end of a question."""
    context = f"<case_id:{case_id}, folder_id:{folder_id}>"
    return f"{question} {context}"


def process_json_file(file_path: Path, case_id: str, folder_id: str) -> bool:
    """Process a single JSON file and update questions with context."""
    try:
        # Read the JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if data is a list
        if not isinstance(data, list):
            print(f"  [WARNING] {file_path.name} does not contain a list, skipping...")
            return False
        
        # Update each question
        updated_count = 0
        for item in data:
            if isinstance(item, dict) and 'question' in item:
                # Check if context already exists
                if '<case_id:' in item['question'] and '<folder_id:' in item['question']:
                    continue  # Skip if already has context
                
                # Add context to question
                item['question'] = add_context_to_question(
                    item['question'], 
                    case_id, 
                    folder_id
                )
                updated_count += 1
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"  [OK] Updated {updated_count} questions in {file_path.name}")
        return True
        
    except json.JSONDecodeError as e:
        print(f"  [ERROR] Invalid JSON in {file_path.name}: {e}")
        return False
    except Exception as e:
        print(f"  [ERROR] Error processing {file_path.name}: {e}")
        return False


def main():
    """Main function to process all JSON files in the raw directory."""
    # Define paths
    raw_dir = Path("datasets/loan_arbitration/raw")
    
    if not raw_dir.exists():
        print(f"Error: Directory {raw_dir} does not exist!")
        return
    
    # Get all JSON files matching case_*.json pattern
    json_files = sorted(raw_dir.glob("case_*.json"))
    
    if not json_files:
        print(f"No case_*.json files found in {raw_dir}")
        return
    
    print(f"Found {len(json_files)} case files to process...\n")
    
    # Process each file
    success_count = 0
    for json_file in json_files:
        # Extract case number and generate IDs
        case_number = extract_case_number(json_file.name)
        if not case_number:
            print(f"  [WARNING] Could not extract case number from {json_file.name}, skipping...")
            continue
        
        case_id = f"case_{case_number}"
        folder_id = generate_folder_id(case_number)
        
        print(f"Processing {json_file.name} (Case ID: {case_id}, Folder ID: {folder_id})...")
        
        if process_json_file(json_file, case_id, folder_id):
            success_count += 1
    
    print(f"\n{'='*60}")
    print(f"Processing complete!")
    print(f"Successfully processed: {success_count}/{len(json_files)} files")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

