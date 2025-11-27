# Graph-R1 Setup & Configuration Answers

## 1. Knowledge Graph Storage: NetworkX (Default) vs Neo4j

### Default Setup: **NetworkX (Custom Simple Code)**
- **Default**: `NetworkXStorage` - A simple in-memory graph using NetworkX library
- **Storage**: Saves to GraphML files (`graph_chunk_entity_relation.graphml`)
- **Location**: `graphr1/storage.py` lines 178-318
- **No external dependencies** needed - works out of the box

### Neo4j Option (Available but Optional)
- **Available**: `Neo4JStorage` - Full Neo4j database integration
- **Location**: `graphr1/kg/neo4j_impl.py`
- **Requires**: 
  - Neo4j database running
  - Environment variables: `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`
- **Usage**: Set `graph_storage="Neo4JStorage"` when initializing GraphR1

### Other Available Options:
- **KV Storage**: `JsonKVStorage` (default), `MongoKVStorage`, `OracleKVStorage`, `TiDBKVStorage`
- **Vector Storage**: `NanoVectorDBStorage` (default), `ChromaVectorDBStorage`, `MilvusVectorDBStorge`, `OracleVectorDBStorage`
- **Graph Storage**: `NetworkXStorage` (default), `Neo4JStorage`, `OracleGraphStorage`

**Code Reference** (`graphr1/graphr1.py` lines 121-123):
```python
kv_storage: str = field(default="JsonKVStorage")
vector_storage: str = field(default="NanoVectorDBStorage")
graph_storage: str = field(default="NetworkXStorage")  # <-- Default is NetworkX
```

---

## 2. Gemma3 Support & Tool Calling

### Model Support Status
- **Gemma Config Supported**: Yes (`GemmaConfig` in `verl/models/registry.py` line 22)
- **Gemma2 Support**: Explicitly mentioned in code (`gemma-2-2b-it`)
- **Gemma3**: Not explicitly tested, but architecture should work if it follows Gemma2 patterns

### Tool Calling Mechanism
**Graph-R1 uses a custom tool calling format, NOT standard function calling:**

1. **Format**: The model generates queries in XML-like tags:
   ```xml
   <query>
   {"query": "your search statement"}
   </query>
   ```

2. **Not Standard Function Calling**: This is a **text-based tool call format**, not the JSON function calling API
   - Works with any model that can follow instructions
   - No special function calling capabilities required
   - Model just needs to generate text in the correct format

3. **How It Works** (`agent/tool/tool_env.py` lines 369-399):
   - Model generates text with `<query>...</query>` tags
   - `extract_tool_call()` parses the text using regex
   - Tool environment executes the query
   - Results are fed back to the model

4. **Training Process** (`agent/llm_agent/generation.py`):
   - Model learns to generate queries through RL training
   - Reward based on answer quality (F1, EM scores)
   - No pre-existing function calling needed

### Can You Use Gemma3?
**Yes, but with considerations:**
- ✅ **Architecture**: Should work if Gemma3 follows Gemma2 architecture
- ✅ **Tool Calling**: No special function calling needed - just text generation
- ⚠️ **Testing**: You may need to verify:
  - Tokenizer compatibility
  - Chat template format
  - Generation quality

**To use Gemma3**, modify the model path in training scripts:
```bash
# In run_grpo.sh or run_ppo.sh
export BASE_MODEL="google/gemma-3-XX"  # Replace with actual Gemma3 model path
```

---

## 3. FAISS Usage in Graph-R1

### Where FAISS is Used

**FAISS is used for fast vector similarity search** in the retrieval API server:

1. **During Knowledge Graph Building** (`script_build.py`):
   - Creates FAISS indices for:
     - **Text chunks** (`index.bin`)
     - **Entities** (`index_entity.bin`) 
     - **Hyperedges** (`index_hyperedge.bin`)
   - Uses `BAAI/bge-large-en-v1.5` embeddings
   - Stores in `expr/{data_source}/` directory

2. **During Training/Inference** (`script_api.py`):
   - **Retrieval API Server** (port 8001) uses FAISS for:
     - Fast entity matching
     - Fast hyperedge matching
   - When model generates a query, FAISS quickly finds relevant entities/hyperedges
   - Then queries the knowledge graph with those matches

### FAISS Workflow:
```
Model generates query → FAISS searches embeddings → Finds top-k entities/hyperedges → 
Graph query with matches → Returns subgraph → Model uses subgraph to answer
```

### FAISS vs NanoVectorDB
- **FAISS**: Used in the **retrieval API** for fast similarity search (pre-built indices)
- **NanoVectorDB**: Used during **graph construction** for storing embeddings incrementally
- Both serve different purposes in the pipeline

**Code Locations**:
- `script_build.py` lines 78-106: Building FAISS indices
- `script_api.py` lines 27-43: Loading and using FAISS indices
- `agent/tool/tools/search_tool.py`: Uses the FAISS-backed API

---

## 4. Large Data Ingestion: Step-by-Step Process

### Overview: How Data Flows into the Graph

```
Raw Documents → Chunking → Entity Extraction → Knowledge Graph → FAISS Indexing
```

### Step-by-Step Process

#### **Step 1: Prepare Your Data**
Your data should be in JSONL format with `contents` field:
```json
{"contents": "Your large document text here..."}
{"contents": "Another document..."}
```

#### **Step 2: Process Data** (`script_process.py`)
```bash
python script_process.py --data_source YourDataset
```
- Converts raw QA data to parquet format
- Creates training/validation splits

#### **Step 3: Build Knowledge Graph** (`script_build.py`)
```bash
python script_build.py --data_source YourDataset
```

**What happens** (`script_build.py` lines 108-114):
1. **Initialize GraphR1**:
   ```python
   rag = GraphR1(working_dir=f"expr/{data_source}")
   ```

2. **Insert Documents** (lines 11-40):
   - Reads from `datasets/{data_source}/corpus.jsonl`
   - **Chunks documents** (default: 1200 tokens, 100 overlap)
   - **Extracts entities** using GPT-4o-mini (or your LLM)
   - **Builds knowledge hypergraph** with n-ary relations
   - Processes in batches of 50 documents

3. **Embed Knowledge** (lines 42-106):
   - Generates embeddings for:
     - Text chunks
     - Entities  
     - Hyperedges
   - Creates FAISS indices for fast retrieval

#### **Step 4: For Large Datasets - Batch Processing**

**The code already handles batching** (`script_build.py` lines 12-26):
```python
# Processes 50 documents at a time
for i in range(0, len(unique_contexts), 50):
    rag.insert(unique_contexts[i:i+50])
```

**For very large datasets, you can:**
1. **Modify batch size** (line 13): Change `50` to your preferred batch size
2. **Process incrementally**: Run `script_build.py` multiple times with different data splits
3. **Use custom KG insertion**:
   ```python
   from graphr1 import GraphR1
   
   rag = GraphR1(working_dir="your_working_dir")
   
   # Insert large chunks
   large_documents = ["doc1...", "doc2...", ...]
   rag.insert(large_documents)  # Handles chunking automatically
   ```

#### **Step 5: Storage Locations**

After ingestion, data is stored in:
```
expr/{data_source}/
├── kv_store_text_chunks.json      # Document chunks
├── kv_store_entities.json          # Extracted entities
├── kv_store_hyperedges.json         # Relationships
├── graph_chunk_entity_relation.graphml  # Knowledge graph
├── index.bin                       # FAISS index for chunks
├── index_entity.bin                # FAISS index for entities
└── index_hyperedge.bin             # FAISS index for hyperedges
```

### Custom Knowledge Graph Insertion

If you have pre-processed knowledge, use `insert_custom_kg()`:
```python
rag = GraphR1(working_dir="your_dir")

custom_kg = {
    "chunks": [
        {"content": "...", "source_id": "..."}
    ],
    "entities": [
        {"entity_name": "...", "entity_type": "...", "description": "...", "source_id": "..."}
    ],
    "relationships": [
        {"src_id": "...", "tgt_id": "...", "description": "...", "keywords": "...", "weight": 1.0, "source_id": "..."}
    ]
}

rag.insert_custom_kg(custom_kg)
```

### Memory Considerations

- **NetworkX (default)**: In-memory graph - limited by RAM
- **For very large graphs**: Consider Neo4j or Oracle backend
- **Chunking**: Default 1200 tokens - adjust based on your needs
- **Batch processing**: Already implemented to handle large datasets

---

## Summary

1. **KG Setup**: Default is **NetworkX** (simple, no dependencies). Neo4j available as option.
2. **Gemma3**: Should work, but needs testing. Tool calling is text-based, not function calling.
3. **FAISS**: Used for fast vector search in retrieval API (port 8001).
4. **Large Data**: Batch processing already implemented. Use `script_build.py` or `rag.insert()` directly.

