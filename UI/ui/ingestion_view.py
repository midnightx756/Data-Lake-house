from tkinter import ttk, filedialog, messagebox
from ui.widgets import heading
class IngestionFrame(ttk.Frame):
    def __init__(self,parent,app):
        super().__init__(parent); self.app=app
        heading(self,"Ingestion Pipeline","Scan a folder into SQLite metadata; original files are not moved.")
        row=ttk.Frame(self); row.pack(fill="x",pady=8)
        self.path=ttk.Entry(row); self.path.pack(side="left",fill="x",expand=True,padx=(0,6))
        ttk.Button(row,text="Browse…",command=self.browse).pack(side="left")
        ttk.Button(self,text="Start background scan",style="Accent.TButton",command=self.start).pack(anchor="w",pady=8)
        self.output=ttk.Label(self,text="Ready"); self.output.pack(anchor="w",pady=8)
        ttk.Button(self,text="Cancel current scan",command=self.cancel).pack(anchor="w")
        self.after(500,self.poll)
    def browse(self):
        path=filedialog.askdirectory()
        if path: self.path.delete(0,"end"); self.path.insert(0,path)
    def start(self):
        from services.ingestion_service import scan_request
        try:
            if scan_request(self.path.get(),self.app.jobs): self.output.config(text="Scan queued…")
            else: messagebox.showinfo("SDLH","A scan is already queued or running.")
        except Exception as e: messagebox.showerror("Invalid folder",str(e))
    def cancel(self): self.app.jobs.cancel(); self.output.config(text="Cancellation requested")
    def poll(self):
        job=self.app.jobs
        text=f"Status: {job.status} — {job.message}"
        if job.last_result: text += f" | {job.last_result}"
        self.output.config(text=text)
        self.after(500,self.poll)
