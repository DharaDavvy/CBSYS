"""Full ChromaDB pipeline test — default embedding function."""
import os, sys, shutil

LOG = os.path.join(os.path.dirname(__file__), "..", "test_result.txt")
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "test_chroma3")

def log(msg):
    print(msg, flush=True)
    with open(LOG, "a") as f:
        f.write(msg + "\n")

# Reset
with open(LOG, "w") as f:
    f.write("")
if os.path.exists(DB_PATH):
    shutil.rmtree(DB_PATH)

try:
    log("1. Import chromadb...")
    import chromadb
    log(f"   v{chromadb.__version__}")

    log("2. Create persistent client...")
    c = chromadb.PersistentClient(path=DB_PATH)

    log("3. Create collection (default embeddings)...")
    col = c.get_or_create_collection("test_col")

    log("4. col.add()...")
    col.add(documents=["hello world document"], ids=["id1"])
    log("   ADD OK")

    log("5. col.query()...")
    res = col.query(query_texts=["hello"], n_results=1)
    log(f"   QUERY OK: {res['documents']}")

    log("SUCCESS")
except Exception as e:
    import traceback
    log(f"FAILED: {type(e).__name__}: {e}")
    with open(LOG, "a") as f:
        traceback.print_exc(file=f)
