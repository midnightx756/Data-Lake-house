import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from ui.widgets import heading
from ui.theme import PANEL
from ui.asset_viewer import open_blob_asset_viewer
from database.connection import get_connection
from core.cpp_blob_bridge import pack_to_blob


class StorageFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        heading(self, "C++ Blob Storage", "Inspect packed .blob records or extract any asset via mmap().")
        ttk.Label(
            self,
            text="Folders scanned in Ingestion are packed here automatically. Double-click any row to view via mmap().",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(0, 12))

        row = ttk.Frame(self)
        row.pack(fill="x", pady=5)
        ttk.Button(row, text="Extract & View (mmap)", style="Accent.TButton", command=self.extract_selected).pack(side="left")
        ttk.Button(row, text="Pack extra files manually", command=self.pack_files).pack(side="left", padx=8)
        ttk.Button(row, text="Refresh manifest records", command=self.refresh).pack(side="left")

        self.output = tk.Text(
            self, height=8, bg=PANEL, fg="#eef3fb", insertbackground="#eef3fb",
            relief="flat", wrap="word", font=("Consolas", 9),
        )
        self.output.pack(fill="x", pady=10)

        ttk.Label(self, text="Packed assets registered in SQLite", font=("Segoe UI Semibold", 13)).pack(anchor="w", pady=(10, 2))
        self.table = ttk.Treeview(
            self,
            columns=("source_path", "blob_path", "byte_offset", "payload_size", "is_duplicate"),
            show="headings",
            height=12,
        )
        for col, title, width in [
            ("source_path", "SOURCE FILE", 300),
            ("blob_path", "BLOB FILE", 250),
            ("byte_offset", "OFFSET", 90),
            ("payload_size", "PAYLOAD BYTES", 120),
            ("is_duplicate", "DEDUP", 70),
        ]:
            self.table.heading(col, text=title)
            self.table.column(col, width=width, anchor="w")
        self.table.pack(fill="both", expand=True, pady=6)
        self.table.bind("<Double-1>", lambda _e: self.extract_selected())
        self.refresh()

    def pack_files(self):
        paths = filedialog.askopenfilenames(title="Choose files to pack")
        if not paths:
            return
        blob = filedialog.asksaveasfilename(
            title="Save new blob",
            defaultextension=".blob",
            filetypes=[("SDLH blob", "*.blob")],
            initialfile="sdlh_storage.blob",
        )
        if not blob:
            return
        manifest = str(Path(blob).with_suffix(".manifest.csv"))
        try:
            result = pack_to_blob(paths, blob, manifest)
            self.output.delete("1.0", "end")
            self.output.insert(
                "end",
                result["stdout"] + f'\nManifest rows imported to SQLite: {result["manifest_rows"]}\nManifest: {manifest}',
            )
            self.refresh()
            messagebox.showinfo("Blob pack complete", "Files packed via bin/sdlh.")
        except Exception as e:
            messagebox.showerror("C++ blob integration", str(e))

    def extract_selected(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showinfo("Extract", "Click a row in the table first.")
            return
        source_path, blob_path, byte_offset, *_ = self.table.item(selected[0], "values")
        open_blob_asset_viewer(self, Path(source_path).name, source_path, blob_path, byte_offset)

    def refresh(self):
        self.table.delete(*self.table.get_children())
        try:
            with get_connection() as conn:
                rows = conn.execute(
                    "SELECT source_path,blob_path,byte_offset,payload_size,is_duplicate "
                    "FROM blob_assets ORDER BY blob_asset_id DESC LIMIT 500"
                ).fetchall()
            for row in rows:
                self.table.insert("", "end", values=tuple(row))
        except Exception:
            pass
