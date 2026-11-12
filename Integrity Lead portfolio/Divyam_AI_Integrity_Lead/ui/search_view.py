from tkinter import ttk, messagebox
from ui.widgets import heading, tree, fill_tree
from core.semantic_search import semantic_search, index_images


class SearchFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        heading(
            self,
            "Content Search",
            "Index images with CLIP, then search using ordinary text."
        )

        bar = ttk.Frame(self)
        bar.pack(fill="x")

        ttk.Button(
            bar, text="Index Images with CLIP", command=self.run_index
        ).pack(side="left", padx=(0, 6))

        self.q = ttk.Entry(bar)
        self.q.pack(side="left", fill="x", expand=True, padx=(0, 6))

        ttk.Button(
            bar, text="Search", command=self.run_search
        ).pack(side="left")

        self.cols = ("asset_id", "name", "extension", "path")
        self.view = tree(self, self.cols, ("ID", "Name", "Type", "Path"))

    def run_index(self):
        try:
            result = index_images()
            messagebox.showinfo(
                "CLIP indexing",
                f'Images indexed: {result["indexed"]}\n'
                f'Files skipped: {result["skipped"]}'
            )
        except Exception as error:
            messagebox.showerror("CLIP indexing failed", str(error))

    def run_search(self):
        try:
            results = semantic_search(self.q.get())
            fill_tree(self.view, results, self.cols)
        except Exception as error:
            messagebox.showerror("Search failed", str(error))
