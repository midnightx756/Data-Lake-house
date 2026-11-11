from tkinter import ttk
class AboutFrame(ttk.Frame):
    def __init__(self,parent,app):
        super().__init__(parent)
        ttk.Label(self,text="Semantic Data Lakehouse",font=("Segoe UI",20,"bold")).pack(anchor="w")
        ttk.Label(self,text="Third-year CSE demonstrator: metadata, ingestion, DBMS, integrity and search.").pack(anchor="w",pady=8)
