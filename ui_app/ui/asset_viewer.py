"""In-app viewer for assets extracted straight from .blob via C++ mmap."""
import io
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from ui.theme import BG, PANEL, PANEL_ALT, TEXT, ACCENT, MUTED
from core.cpp_blob_bridge import extract_asset_bytes

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}
TEXT_EXTS = {
    ".txt", ".md", ".csv", ".json", ".xml", ".py", ".sql", ".log",
    ".html", ".htm", ".css", ".js", ".c", ".cpp", ".h", ".hpp", ".sh",
}


def open_blob_asset_viewer(parent, name, source_path, blob_path, byte_offset):
    try:
        raw_bytes, cpp_log = extract_asset_bytes(blob_path, byte_offset)
    except Exception as exc:
        messagebox.showerror("mmap Extraction Failed", str(exc))
        return

    win = tk.Toplevel(parent)
    win.title(f"Extracted via mmap() — {name}")
    win.geometry("780x580")
    win.configure(bg=BG)

    header = tk.Frame(win, bg=PANEL, padx=14, pady=10)
    header.pack(fill="x")
    tk.Label(header, text=name, bg=PANEL, fg=ACCENT, font=("Segoe UI Semibold", 14)).pack(anchor="w")
    info = (
        f"Blob: {blob_path}   |   Byte Offset: {byte_offset}   |   "
        f"Extracted: {len(raw_bytes):,} bytes"
    )
    tk.Label(header, text=info, bg=PANEL, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", pady=(2, 0))
    if cpp_log:
        tk.Label(header, text=cpp_log.strip(), bg=PANEL, fg="#4fd1a5", font=("Consolas", 8)).pack(anchor="w", pady=(4, 0))

    body = tk.Frame(win, bg=BG, padx=14, pady=10)
    body.pack(fill="both", expand=True)

    ext = Path(name or source_path).suffix.lower()
    rendered = False

    if ext in IMAGE_EXTS:
        try:
            from PIL import Image, ImageTk

            img = Image.open(io.BytesIO(raw_bytes))
            img.thumbnail((720, 400))
            photo = ImageTk.PhotoImage(img)
            lbl = tk.Label(body, image=photo, bg=PANEL)
            lbl.pack(fill="both", expand=True)
            win._img_ref = photo  # prevent GC
            rendered = True
        except Exception:
            rendered = False

    if not rendered:
        box = tk.Text(
            body, bg=PANEL, fg=TEXT, insertbackground=TEXT,
            relief="flat", wrap="word", font=("Consolas", 10), padx=10, pady=10
        )
        box.pack(fill="both", expand=True)
        if ext in TEXT_EXTS or b"\x00" not in raw_bytes[:512]:
            box.insert("1.0", raw_bytes.decode("utf-8", errors="replace"))
        else:
            preview_len = min(len(raw_bytes), 512)
            hex_lines = []
            for i in range(0, preview_len, 16):
                chunk = raw_bytes[i:i + 16]
                hx = " ".join(f"{b:02x}" for b in chunk)
                asc = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
                hex_lines.append(f"{i:04x}: {hx:<48}  {asc}")
            box.insert(
                "1.0",
                f"[Binary payload: {len(raw_bytes):,} bytes — first {preview_len} bytes hex dump]\n\n"
                + "\n".join(hex_lines),
            )
        box.config(state="disabled")

    footer = tk.Frame(win, bg=BG, padx=14, pady=8)
    footer.pack(fill="x")

    def save_copy():
        out = filedialog.asksaveasfilename(title="Export copy", initialfile=name)
        if out:
            Path(out).write_bytes(raw_bytes)
            messagebox.showinfo("Saved", f"Saved copy to:\n{out}")

    ttk.Button(footer, text="Export copy to disk (optional)", command=save_copy).pack(side="left")
    ttk.Button(footer, text="Close", command=win.destroy).pack(side="right")
