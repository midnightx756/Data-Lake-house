from tkinter import ttk, messagebox
from ui.widgets import heading, tree, fill_tree
from database.queries import table_names, table_info
from services.db_service import run_readonly_query
class DBMSFrame(ttk.Frame):
    def __init__(self,parent,app):
        super().__init__(parent); heading(self,"DBMS Console","Inspect SQLite schema or run read-only SELECT/PRAGMA queries.")
        self.tables=ttk.Combobox(self,values=table_names(),state="readonly"); self.tables.pack(anchor="w",fill="x")
        self.tables.bind("<<ComboboxSelected>>",self.show_schema)
        self.sql=ttk.Entry(self); self.sql.pack(fill="x",pady=8); self.sql.insert(0,"SELECT name, extension, size_bytes FROM assets LIMIT 50")
        ttk.Button(self,text="Run read-only query",command=self.run_query).pack(anchor="w")
        self.view=tree(self,("a","b","c"),("Column / Key","Type / Value","Details"))
    def show_schema(self,event=None):
        rows=table_info(self.tables.get()); fill_tree(self.view,[{"a":r["name"],"b":r["type"],"c":f'notnull={r["notnull"]}, pk={r["pk"]}'} for r in rows],("a","b","c"))
    def run_query(self):
        try:
            rows=run_readonly_query(self.sql.get()); cols=list(rows[0].keys())[:3] if rows else ["Result","",""]
            self.view["columns"]=("a","b","c")
            fill_tree(self.view,[{"a":str(list(r.values())[0]) if len(r)>0 else "",
                                  "b":str(list(r.values())[1]) if len(r)>1 else "",
                                  "c":str(list(r.values())[2]) if len(r)>2 else ""} for r in rows],("a","b","c"))
        except Exception as e: messagebox.showerror("Query rejected",str(e))
