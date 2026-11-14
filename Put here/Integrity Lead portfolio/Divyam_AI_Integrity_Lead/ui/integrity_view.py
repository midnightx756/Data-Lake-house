from tkinter import ttk, messagebox
from ui.widgets import heading, tree, fill_tree
from services.integrity_service import (
    run_integrity_check,
    run_blob_integrity_check,
)


class IntegrityFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        heading(
            self,
            "Integrity & Deduplication",
            "Check original files and packed blob data."
        )

        buttons = ttk.Frame(self)
        buttons.pack(anchor="w", pady=6)

        ttk.Button(
            buttons,
            text="Check Original Files",
            command=self.run
        ).pack(side="left", padx=(0, 6))

        ttk.Button(
            buttons,
            text="Check Blob Integrity",
            command=self.run_blob_check
        ).pack(side="left")

        self.summary = ttk.Label(self, text="Not run")
        self.summary.pack(anchor="w", pady=6)

        self.view = tree(self, ("path", "issue"), ("Path", "Issue"))

    def run(self):
        result = run_integrity_check()
        self.summary.config(
            text=f'Original files: checked {result["checked"]} • '
                 f'missing {result["missing"]} • changed {result["changed"]}'
        )
        rows = [
            {"path": path, "issue": issue}
            for path, issue in result["problems"]
        ]
        fill_tree(self.view, rows, ("path", "issue"))

    def run_blob_check(self):
        try:
            result = run_blob_integrity_check()
            self.summary.config(
                text=f'Blob records: checked {result["checked"]} • '
                     f'valid {result["valid"]} • '
                     f'corrupted {result["corrupted"]} • '
                     f'errors {result["errors"]}'
            )
            rows = [
                {"path": path, "issue": issue}
                for path, issue in result["problems"]
            ]
            fill_tree(self.view, rows, ("path", "issue"))
        except Exception as error:
            messagebox.showerror("Blob integrity check failed", str(error))
