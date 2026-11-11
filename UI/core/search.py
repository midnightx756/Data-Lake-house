from database.repository import AssetRepository
def search_assets(query, extension="", limit=500):
    return AssetRepository().search(query,extension,limit)
