import sqlite3
from tkinter import ttk, messagebox
from ui.widgets import heading
from ui.asset_viewer import open_blob_asset_viewer
from core.search import search_assets
from database.connection import get_connection


class ExplorerFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        heading(self, "Data Explorer", "Browse indexed files and extract directly from C++ blobs via mmap().")

        bar = ttk.Frame(self)
        bar.pack(fill="x")
        self.query = ttk.Entry(bar)
        self.query.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ttk.Button(bar, text="Search", command=self.refresh).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text="Extract & View (mmap)", style="Accent.TButton", command=self.extract_selected).pack(side="left")

        cols = ("asset_id", "name", "extension", "size_bytes", "byte_offset", "is_duplicate")
        heads = ("ID", "Name", "Type", "Bytes", "Blob Offset", "Duplicate")
        self.view = ttk.Treeview(self, columns=cols, show="headings")
        for col, title in zip(cols, heads):
            self.view.heading(col, text=title)
            self.view.column(col, width=120, anchor="w")
        self.view.pack(fill="both", expand=True, pady=8)
        self.view.bind("<Double-1>", lambda _e: self.extract_selected())

        self._meta = {}
        self.refresh()

    def refresh(self):
        rows = search_assets(self.query.get(), limit=1000)
        blob_map = {}
        try:
            with get_connection() as conn:
                for b in conn.execute("SELECT source_path, blob_path, byte_offset FROM blob_assets").fetchall():
                    blob_map[b["source_path"]] = (b["blob_path"], b["byte_offset"])
        except sqlite3.OperationalError:
            pass

        self.view.delete(*self.view.get_children())
        self._meta.clear()
        for r in rows:
            blob_info = blob_map.get(r["path"])
            offset_display = blob_info[1] if blob_info else "Not packed"
            iid = self.view.insert(
                "", "end",
                values=(r["asset_id"], r["name"], r["extension"], r["size_bytes"], offset_display, r["is_duplicate"]),
            )
            self._meta[iid] = (r["name"], r["path"], blob_info)

    def extract_selected(self):
        sel = self.view.selection()
        if not sel:
            messagebox.showinfo("Explorer", "Select a file row first (or double-click it).")
            return
        name, path, blob_info = self._meta[sel[0]]
        if not blob_info:
            messagebox.showinfo(
                "Not in a blob yet",
                "This file was scanned before auto-packing was enabled.\nRe-scan its folder in Ingestion to pack it into a blob.",
            )
            return
        blob_path, byte_offset = blob_info
        open_blob_asset_viewer(self, name, path, blob_path, byte_offset)
