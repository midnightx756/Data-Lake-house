from database.repository import AssetRepository
def storage_summary():
    s=AssetRepository().stats()
    s["size_mb"]=round(s["bytes"]/1024/1024,2)
    return s
