from tkinter import ttk
from ui.widgets import heading, tree, fill_tree
from core.semantic_search import semantic_search
class SearchFrame(ttk.Frame):
    def __init__(self,parent,app):
        super().__init__(parent); heading(self,"Content Search","Keyword search over names, paths and extracted text; embeddings are not enabled by default.")
        bar=ttk.Frame(self); bar.pack(fill="x")
        self.q=ttk.Entry(bar); self.q.pack(side="left",fill="x",expand=True,padx=(0,6))
        ttk.Button(bar,text="Search",command=self.run_search).pack(side="left")
        self.cols=("asset_id","name","extension","path")
        self.view=tree(self,self.cols,("ID","Name","Type","Path"))
    def run_search(self):
        fill_tree(self.view,semantic_search(self.q.get()),self.cols)
