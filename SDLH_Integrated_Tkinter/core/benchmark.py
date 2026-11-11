import time, tempfile
from pathlib import Path
from database.repository import AssetRepository
def query_benchmark(iterations=100):
    repo=AssetRepository(); start=time.perf_counter()
    for _ in range(iterations): repo.search("a",limit=100)
    elapsed=time.perf_counter()-start
    return {"iterations":iterations,"elapsed_seconds":round(elapsed,4),
            "avg_ms":round(elapsed*1000/iterations,3) if iterations else 0,
            "records":repo.stats()["assets"]}
