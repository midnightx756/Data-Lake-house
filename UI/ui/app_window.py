import tkinter as tk
from tkinter import ttk
from ui.theme import apply_theme, BG, PANEL, ACCENT, MUTED
from ui.dashboard import DashboardFrame
from ui.explorer import ExplorerFrame
from ui.ingestion_view import IngestionFrame
from ui.search_view import SearchFrame
from ui.dbms_view import DBMSFrame
from ui.integrity_view import IntegrityFrame
from ui.benchmark_view import BenchmarkFrame
from ui.settings_view import SettingsFrame
from ui.storage_view import StorageFrame
from core.jobs import JobManager

class SDLHApplication:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Semantic Data Lakehouse | SDLH")
        self.root.geometry("1280x800")
        self.root.minsize(1000, 650)
        apply_theme(self.root)
        self.jobs = JobManager()

        self.shell = ttk.Frame(self.root)
        self.shell.pack(fill="both", expand=True)

        self.sidebar = ttk.Frame(self.shell, style="Sidebar.TFrame", padding=(14, 18))
        self.sidebar.pack(side="left", fill="y")
        brand = tk.Frame(self.sidebar, bg="#0b1220")
        brand.pack(fill="x", pady=(2, 24))
        tk.Label(brand, text="SDLH", bg="#0b1220", fg=ACCENT,
                 font=("Segoe UI Black", 25)).pack(anchor="w")
        tk.Label(brand, text="SEMANTIC DATA LAKEHOUSE", bg="#0b1220", fg=MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(2, 0))
        ttk.Separator(self.sidebar).pack(fill="x", pady=(0, 16))

        self.body = ttk.Frame(self.shell, padding=(24, 18))
        self.body.pack(side="left", fill="both", expand=True)

        top = ttk.Frame(self.body)
        top.pack(fill="x", pady=(0, 14))
        self.page_title = ttk.Label(top, text="Overview", style="Title.TLabel")
        self.page_title.pack(side="left")
        self.mode_label = tk.Label(top, text="●  LOCAL CPU MODE",
                                   bg=BG, fg="#4fd1a5",
                                   font=("Segoe UI", 9, "bold"))
        self.mode_label.pack(side="right", padx=4)

        self.content = ttk.Frame(self.body)
        self.content.pack(fill="both", expand=True)

        self.views = [
            ("Dashboard", "Overview", DashboardFrame),
            ("Explorer", "Data Explorer", ExplorerFrame),
            ("Ingestion", "Ingestion Pipeline", IngestionFrame),
            ("Search", "Content Search", SearchFrame),
            ("DBMS", "Database Manager", DBMSFrame),
            ("Integrity", "Integrity & Deduplication", IntegrityFrame),
            ("Benchmark", "Benchmark Lab", BenchmarkFrame),
            ("Storage", "C++ Blob Storage", StorageFrame),
                ("Settings", "Settings & Backup", SettingsFrame),
        ]
        self.nav_buttons = {}
        for label, title, cls in self.views:
            btn = ttk.Button(self.sidebar, text="   " + label,
                             style="Nav.TButton",
                             command=lambda c=cls, t=title: self.show(c, t))
            btn.pack(fill="x", pady=3)
            self.nav_buttons[label] = btn

        footer = tk.Frame(self.sidebar, bg="#0b1220")
        footer.pack(side="bottom", fill="x", pady=(20, 0))
        tk.Label(footer, text="THIRD-YEAR CSE PROJECT", bg="#0b1220", fg=MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w")
        tk.Label(footer, text="Metadata • DBMS • OS • Search", bg="#0b1220", fg=MUTED,
                 font=("Segoe UI", 8)).pack(anchor="w", pady=(4, 0))
        self.status = tk.StringVar(value="Ready")
        ttk.Label(self.body, textvariable=self.status, style="Muted.TLabel").pack(anchor="w", pady=(8, 0))
        self.show(DashboardFrame, "Overview")

    def show(self, cls, title):
        for child in self.content.winfo_children():
            child.destroy()
        self.page_title.config(text=title)
        frame = cls(self.content, self)
        frame.pack(fill="both", expand=True)
        self.status.set(f"{title}  •  Local database connected")

    def run(self):
        self.root.mainloop()
