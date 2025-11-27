"""
Script to create corpus.jsonl from case files and arbitration document
for Graph-R1 knowledge graph ingestion
"""

import os
import json
from pathlib import Path

def read_markdown_file(file_path):
    """Read a markdown file and return its contents"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def create_corpus_jsonl():
    """Create corpus.jsonl from all case files and arbitration document"""
    
    # Define paths
    base_dir = Path("dataset/dataset")
    cases_dir = base_dir / "cases"
    arbitration_file = base_dir / "perplexity-Arbitration and Conc.md"
    output_file = Path("datasets/loan_arbitration/corpus.jsonl")
    
    # Create output directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # List to store all documents
    documents = []
    
    # Read all case files (case_001.md to case_050.md)
    print("Reading case files...")
    case_files = sorted(cases_dir.glob("case_*.md"))
    
    if not case_files:
        print(f"Warning: No case files found in {cases_dir}")
    else:
        print(f"Found {len(case_files)} case files")
        
        for case_file in case_files:
            content = read_markdown_file(case_file)
            if content:
                # Extract case number from filename for metadata
                case_num = case_file.stem.replace("case_", "")
                documents.append({
                    "contents": content,
                    "source": "case_file",
                    "case_id": case_num,
                    "filename": case_file.name
                })
                print(f"  [OK] Added {case_file.name}")
    
    # Read the arbitration document
    print("\nReading arbitration document...")
    if arbitration_file.exists():
        content = read_markdown_file(arbitration_file)
        if content:
            documents.append({
                "contents": content,
                "source": "arbitration_act",
                "filename": arbitration_file.name
            })
            print(f"  [OK] Added {arbitration_file.name}")
    else:
        print(f"Warning: Arbitration file not found at {arbitration_file}")
    
    # Write to corpus.jsonl
    print(f"\nWriting {len(documents)} documents to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        for doc in documents:
            # Write as JSON line (only contents field as per script_build.py format)
            json_line = json.dumps({"contents": doc["contents"]}, ensure_ascii=False)
            f.write(json_line + '\n')
    
    print(f"\n[SUCCESS] Successfully created corpus.jsonl with {len(documents)} documents")
    print(f"  Output: {output_file}")
    print(f"  Total size: {output_file.stat().st_size / 1024:.2f} KB")
    
    # Print summary
    print("\nSummary:")
    print(f"  - Case files: {len([d for d in documents if d['source'] == 'case_file'])}")
    print(f"  - Arbitration document: {len([d for d in documents if d['source'] == 'arbitration_act'])}")
    print(f"  - Total documents: {len(documents)}")

if __name__ == "__main__":
    create_corpus_jsonl()

