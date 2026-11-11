from tkinter import ttk, messagebox
from ui.widgets import heading, tree, fill_tree
from services.integrity_service import run_integrity_check
class IntegrityFrame(ttk.Frame):
    def __init__(self,parent,app):
        super().__init__(parent); heading(self,"Integrity & Deduplication","Checks stored paths, file sizes and SHA-256 hashes.")
        ttk.Button(self,text="Run integrity check (first 1,000 assets)",command=self.run).pack(anchor="w",pady=6)
        self.summary=ttk.Label(self,text="Not run"); self.summary.pack(anchor="w",pady=6)
        self.view=tree(self,("path","issue"),("Path","Issue"))
    def run(self):
        result=run_integrity_check()
        self.summary.config(text=f'Checked {result["checked"]} • missing {result["missing"]} • changed {result["changed"]}')
        fill_tree(self.view,[{"path":p,"issue":issue} for p,issue in result["problems"]],("path","issue"))
