"""Quick test: verify ChromaDB default (ONNX) embeddings work."""
import sys
import os

# Prevent ChromaDB from trying to check for model updates online
os.environ["CHROMA_ANONYMIZED_TELEMETRY"] = "false"

LOG = os.path.join(os.path.dirname(__file__), "..", "test_result.txt")

def log(msg):
    print(msg, flush=True)
    with open(LOG, "a") as f:
        f.write(msg + "\n")

# Clear previous log
with open(LOG, "w") as f:
    f.write("")

log("Step 1: importing chromadb...")
try:
    import chromadb
    from chromadb.utils.embedding_functions.onnx_mini_lm_l6_v2 import ONNXMiniLM_L6_V2
    log(f"  chromadb {chromadb.__version__} imported")
except Exception as e:
    log(f"  FAIL: {e}")
    sys.exit(1)

log("Step 2: creating ONNX embedding function directly...")
ef = ONNXMiniLM_L6_V2(preferred_providers=["CPUExecutionProvider"])

log("Step 3: creating client + collection...")
client = chromadb.Client()
col = client.get_or_create_collection("test", embedding_function=ef)

log("Step 4: adding document...")
try:
    col.add(documents=["hello world"], ids=["1"])
    log("  add succeeded")
except Exception as e:
    log(f"  add FAILED: {type(e).__name__}: {e}")
    import traceback
    with open(LOG, "a") as f:
        traceback.print_exc(file=f)
    sys.exit(1)

log("Step 5: querying...")
try:
    res = col.query(query_texts=["hello"], n_results=1)
    log(f"Result: {res['documents']}")
    log("SUCCESS: ONNX embeddings work!")
except Exception as e:
    log(f"  query FAILED: {type(e).__name__}: {e}")
    import traceback
    with open(LOG, "a") as f:
        traceback.print_exc(file=f)
    sys.exit(1)
