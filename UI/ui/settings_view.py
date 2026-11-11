from tkinter import ttk, filedialog, messagebox
from ui.widgets import heading
from core.backup import backup_database
class SettingsFrame(ttk.Frame):
    def __init__(self,parent,app):
        super().__init__(parent); heading(self,"Settings & Backup","Local-only configuration and database backup.")
        ttk.Label(self,text="Database: data/sdlh_metadata.db").pack(anchor="w",pady=4)
        ttk.Button(self,text="Back up database…",command=self.backup).pack(anchor="w",pady=8)
        ttk.Label(self,text="Do not store confidential files in a demo dataset.").pack(anchor="w",pady=4)
    def backup(self):
        path=filedialog.asksaveasfilename(defaultextension=".db",filetypes=[("SQLite database","*.db")])
        if path:
            try: backup_database(path); messagebox.showinfo("Backup","Backup saved.")
            except Exception as e: messagebox.showerror("Backup failed",str(e))
