from core.catalog import list_assets
def catalog_search(query="", extension="", limit=500): return list_assets(query,extension,limit)
