import tkinter as tk
from tkinter import ttk
from ui.widgets import heading
from ui.theme import PANEL, ACCENT, MUTED, TEXT
from analytics.reporting import dashboard_metrics, extension_breakdown

class DashboardFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        heading(self, "Workspace Overview", "Monitor indexed files, metadata storage and data quality.")
        metrics = dashboard_metrics()
        cards = ttk.Frame(self)
        cards.pack(fill="x", pady=(10, 20))
        items = [
            ("INDEXED ASSETS", f'{metrics["assets"]:,}'),
            ("STORAGE SIZE", f'{metrics["bytes"]/1024/1024:.2f} MB'),
            ("FILE TYPES", str(metrics["types"])),
            ("DUPLICATE FLAGS", str(metrics["duplicates"])),
            ("JOBS RECORDED", str(metrics["jobs"])),
        ]
        for label, value in items:
            card = tk.Frame(cards, bg=PANEL, highlightbackground="#2e3d55",
                            highlightthickness=1, padx=14, pady=14)
            card.pack(side="left", fill="both", expand=True, padx=(0, 8))
            tk.Label(card, text=label, bg=PANEL, fg=MUTED,
                     font=("Segoe UI", 8, "bold")).pack(anchor="w")
            tk.Label(card, text=value, bg=PANEL, fg=ACCENT,
                     font=("Segoe UI Semibold", 20)).pack(anchor="w", pady=(9, 2))
        section = ttk.Frame(self)
        section.pack(fill="both", expand=True)
        ttk.Label(section, text="File type distribution",
                  font=("Segoe UI Semibold", 14)).pack(anchor="w", pady=(0, 10))
        rows = extension_breakdown()[:12]
        table = ttk.Treeview(section, columns=("extension", "count", "bytes"),
                             show="headings", height=12)
        for col, title, width in [
            ("extension", "FILE TYPE", 220),
            ("count", "ASSETS", 140),
            ("bytes", "TOTAL BYTES", 180),
        ]:
            table.heading(col, text=title)
            table.column(col, width=width, anchor="w")
        table.pack(fill="both", expand=True)
        for row in rows:
            table.insert("", "end", values=(row["extension"], row["count"], f'{row["bytes"] or 0:,}'))
        ttk.Label(self, text="Tip: scan a small test folder first, then verify it in Explorer.",
                  style="Muted.TLabel").pack(anchor="w", pady=(10, 0))
