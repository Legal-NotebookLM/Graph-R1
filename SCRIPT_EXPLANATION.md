# Script Explanation: script_build.py vs script_process.py

## script_build.py - Graph Building (YOU NEED THIS)

**Purpose**: Builds the knowledge graph from your corpus.jsonl file

**What it does**:
1. Reads `datasets/{data_source}/corpus.jsonl`
2. Uses `GraphR1.insert()` to:
   - Chunk documents
   - Extract entities and relationships (uses OpenAI by default)
   - Build knowledge hypergraph
   - Store in NetworkX (default) or other backends
3. Creates FAISS indices for fast vector search:
   - `index.bin` - for text chunks
   - `index_entity.bin` - for entities
   - `index_hyperedge.bin` - for hyperedges

**Dependencies**:
- `graphr1` package (uses OpenAI for entity extraction by default)
- `FlagEmbedding` (for embeddings)
- `faiss-cpu` (for vector indices)
- `numpy`

**Why aioboto3 is required**:
- `aioboto3` is imported in `graphr1/llm.py` at the **top level** (line 9)
- This means Python tries to import it when loading the module
- It's only actually **used** if you choose AWS Bedrock instead of OpenAI
- **But it must be installed** because of the top-level import
- **Solution**: Install it (it's small and won't affect anything if you use OpenAI)

**Usage**:
```bash
python script_build.py --data_source loan_arbitration
```

---

## script_process.py - Training Data Preparation (YOU DON'T NEED THIS)

**Purpose**: Prepares QA datasets for **training** the RL model (PPO/GRPO)

**What it does**:
1. Reads raw QA datasets (train/dev/test JSON files)
2. Formats them into training prompts with tool-calling instructions
3. Converts to parquet format for training pipeline
4. Creates `train.parquet`, `dev.parquet`, `test.parquet`

**Dependencies**:
- `datasets` (HuggingFace datasets library)
- `pandas` / `pyarrow` (for parquet)

**When you need it**:
- Only if you're going to **train** the RL model
- Not needed for just building the knowledge graph
- Not needed for inference/querying

**Usage** (only if training):
```bash
python script_process.py --data_source loan_arbitration
```

---

## Summary

| Script | Purpose | Needed for Graph Building? |
|--------|---------|---------------------------|
| `script_build.py` | Build knowledge graph | ✅ **YES** |
| `script_process.py` | Prepare training data | ❌ **NO** (only for training) |

---

## Fixing the aioboto3 Import Issue

The `aioboto3` import happens because `graphr1/llm.py` imports it at the top level, even though it's only used for AWS Bedrock. 

**Option 1**: Install it (harmless, won't be used):
```bash
pip install aioboto3
```

**Option 2**: Ignore the import error if you're using OpenAI (default)

**Option 3**: Make it a lazy import (requires code change in graphr1/llm.py)

Since you're using OpenAI (default), you can safely ignore any `aioboto3` import errors - it won't affect graph building.

