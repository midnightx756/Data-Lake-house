from tkinter import ttk, messagebox
from ui.widgets import heading, tree, fill_tree
from core.search import search_assets
class ExplorerFrame(ttk.Frame):
    def __init__(self,parent,app):
        super().__init__(parent); heading(self,"Data Explorer","Browse indexed files and metadata")
        bar=ttk.Frame(self); bar.pack(fill="x")
        self.query=ttk.Entry(bar); self.query.pack(side="left",fill="x",expand=True,padx=(0,6))
        self.query.insert(0,""); ttk.Button(bar,text="Search",command=self.refresh).pack(side="left")
        self.view=tree(self,("asset_id","name","extension","size_bytes","mime_type","is_duplicate"),("ID","Name","Type","Bytes","MIME type","Duplicate"))
        self.refresh()
    def refresh(self):
        rows=search_assets(self.query.get(),limit=1000)
        fill_tree(self.view,rows,("asset_id","name","extension","size_bytes","mime_type","is_duplicate"))
