# Resumption Behavior: What Happens If You Stop and Restart script_build.py

## Good News: It's Smart About Resuming! ✅

The Graph-R1 system has **built-in deduplication and caching** that prevents redundant work:

---

## 1. **Document Deduplication** ✅

**How it works:**
- Each document is hashed using MD5 (`compute_mdhash_id`)
- Before inserting, `filter_keys()` checks what already exists
- **Only new documents are processed**

**Code location:** `graphr1/graphr1.py` lines 278-286
```python
new_docs = {
    compute_mdhash_id(c.strip(), prefix="doc-"): {"content": c.strip()}
    for c in string_or_strings
}
_add_doc_keys = await self.full_docs.filter_keys(list(new_docs.keys()))
new_docs = {k: v for k, v in new_docs.items() if k in _add_doc_keys}
if not len(new_docs):
    logger.warning("All docs are already in the storage")
    return
```

**Result:** If you restart, already-processed documents are **skipped entirely**.

---

## 2. **Chunk Deduplication** ✅

**How it works:**
- Each chunk is also hashed by MD5
- Existing chunks are filtered out before processing
- **Only new chunks go through entity extraction**

**Code location:** `graphr1/graphr1.py` lines 307-315
```python
_add_chunk_keys = await self.text_chunks.filter_keys(
    list(inserting_chunks.keys())
)
inserting_chunks = {
    k: v for k, v in inserting_chunks.items() if k in _add_chunk_keys
}
if not len(inserting_chunks):
    logger.warning("All chunks are already in the storage")
    return
```

**Result:** Already-processed chunks are **skipped**, saving chunking time.

---

## 3. **LLM Response Caching** ✅

**How it works:**
- LLM responses are cached in `llm_response_cache` (JSON file)
- Cache key is based on the prompt hash
- **If the same prompt was processed before, cached response is used**

**Code location:** `graphr1/graphr1.py` lines 195-203, 240-244
```python
self.llm_response_cache = (
    self.key_string_value_json_storage_cls(
        namespace="llm_response_cache",
        ...
    )
    if self.enable_llm_cache  # Default: True
    else None
)

self.llm_model_func = limit_async_func_call(self.llm_model_max_async)(
    partial(
        self.llm_model_func,
        hashing_kv=self.llm_response_cache,  # Cache is passed here
        **self.llm_model_kwargs,
    )
)
```

**Result:** If you restart, **entity extraction for already-processed chunks uses cached LLM responses** - **NO OpenAI API calls** for those!

**Cache location:** `expr/{data_source}/kv_store_llm_response_cache.json`

---

## 4. **Graph Storage Persistence** ✅

**How it works:**
- NetworkX graph is saved to `graph_chunk_entity_relation.graphml`
- When you restart, the graph is **loaded from disk**
- New entities/relations are **added** to existing graph

**Code location:** `graphr1/storage.py` lines 240-249
```python
def __post_init__(self):
    self._graphml_xml_file = os.path.join(
        self.global_config["working_dir"], f"graph_{self.namespace}.graphml"
    )
    preloaded_graph = NetworkXStorage.load_nx_graph(self._graphml_xml_file)
    if preloaded_graph is not None:
        logger.info(
            f"Loaded graph from {self._graphml_xml_file} with {preloaded_graph.number_of_nodes()} nodes, {preloaded_graph.number_of_edges()} edges"
        )
    self._graph = preloaded_graph or nx.Graph()
```

**Result:** Your graph **persists** and continues growing.

---

## 5. **FAISS Index Regeneration** ⚠️

**What happens:**
- `embed_knowledge()` function **always regenerates** FAISS indices
- It reads from existing JSON files (`kv_store_text_chunks.json`, etc.)
- **This is fast** (just embedding + indexing, no LLM calls)

**Code location:** `script_build.py` lines 42-106

**Result:** FAISS indices are rebuilt, but this is:
- ✅ **Fast** (no API calls, just local computation)
- ✅ **Uses existing data** (reads from JSON files, not re-processing)
- ✅ **Necessary** (indices need to include all data)

---

## Summary: What Gets Skipped vs. What Gets Redone

| Component | If Stopped & Restarted | API Calls? |
|-----------|----------------------|------------|
| **Documents** | ✅ Skipped (deduplicated) | ❌ None |
| **Chunks** | ✅ Skipped (deduplicated) | ❌ None |
| **Entity Extraction (LLM)** | ✅ Uses cache | ❌ **NO API calls** for cached |
| **Graph Storage** | ✅ Loaded from disk | ❌ None |
| **FAISS Indices** | ⚠️ Regenerated (but fast) | ❌ None |

---

## Example Scenario

**First Run:**
- Processes 51 documents
- Documents 1-30 complete
- Document 31 in progress (chunked, but entity extraction incomplete)
- You stop the script

**Second Run (Resume):**
1. ✅ Documents 1-30: **Skipped** (already in storage)
2. ✅ Document 31 chunks: **Skipped** (already chunked)
3. ✅ Document 31 entity extraction: **Uses cache** if same chunks were processed
4. ✅ Documents 32-51: **Processed normally**
5. ⚠️ FAISS indices: **Regenerated** (but fast, no API calls)

**Total API calls on resume:** Only for new chunks that weren't cached!

---

## How to Verify Caching is Working

Check these files after a run:
```bash
# LLM cache (saves API calls)
expr/loan_arbitration/kv_store_llm_response_cache.json

# Processed documents
expr/loan_arbitration/kv_store_full_docs.json

# Processed chunks
expr/loan_arbitration/kv_store_text_chunks.json

# Graph
expr/loan_arbitration/graph_chunk_entity_relation.graphml
```

If these files exist and have data, resumption will use them!

---

## Tips for Safe Resumption

1. **Don't delete** the `expr/{data_source}/` folder between runs
2. **Keep** `openai_api_key.txt` the same (cache keys depend on it)
3. **Check logs** - you'll see messages like:
   - "All docs are already in the storage"
   - "All chunks are already in the storage"
   - These mean deduplication is working!

---

## Bottom Line

**✅ Safe to stop and restart!** The system is designed to:
- Skip already-processed documents/chunks
- Use cached LLM responses (saves API costs!)
- Resume from where it left off
- Only regenerate FAISS indices (fast, no API calls)

**You won't waste OpenAI API calls** for already-processed content! 🎉

