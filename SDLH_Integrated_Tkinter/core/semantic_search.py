"""Honest baseline: keyword search over metadata and extracted text.
Embedding/vector search is deliberately optional and not falsely advertised as enabled."""
from core.search import search_assets
def semantic_search(query, limit=100):
    terms=[t.lower() for t in query.split() if len(t)>1]
    rows=search_assets(query,limit=limit)
    if rows or not terms: return rows
    # OR fallback for multiword queries
    found={}
    for term in terms:
        for row in search_assets(term,limit=limit): found[row["asset_id"]]=row
    return list(found.values())[:limit]
