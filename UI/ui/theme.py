"""Modern dark navy + warm yellow ttk theme for the SDLH desktop UI."""
import tkinter as tk
from tkinter import ttk

BG = "#101827"
PANEL = "#182235"
PANEL_ALT = "#202d43"
TEXT = "#eef3fb"
MUTED = "#a8b5c9"
ACCENT = "#f4c542"
ACCENT_DARK = "#d5a91c"
BORDER = "#2e3d55"
GREEN = "#4fd1a5"
RED = "#ff7272"

def apply_theme(root):
    root.configure(bg=BG)
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(".", background=BG, foreground=TEXT, font=("Segoe UI", 10))
    style.configure("TFrame", background=BG)
    style.configure("Panel.TFrame", background=PANEL)
    style.configure("Sidebar.TFrame", background="#0b1220")
    style.configure("TLabel", background=BG, foreground=TEXT)
    style.configure("Muted.TLabel", background=BG, foreground=MUTED)
    style.configure("Title.TLabel", background=BG, foreground=TEXT,
                    font=("Segoe UI Semibold", 22))
    style.configure("Subtitle.TLabel", background=BG, foreground=MUTED,
                    font=("Segoe UI", 10))
    style.configure("Metric.TLabel", background=PANEL, foreground=ACCENT,
                    font=("Segoe UI Semibold", 21))
    style.configure("CardTitle.TLabel", background=PANEL, foreground=MUTED,
                    font=("Segoe UI", 9))
    style.configure("Nav.TButton", background="#0b1220", foreground=TEXT,
                    borderwidth=0, padding=(12, 10), anchor="w",
                    font=("Segoe UI Semibold", 10))
    style.map("Nav.TButton",
              background=[("active", PANEL_ALT), ("pressed", PANEL_ALT)],
              foreground=[("active", ACCENT)])
    style.configure("Accent.TButton", background=ACCENT, foreground="#151515",
                    borderwidth=0, padding=(12, 9), font=("Segoe UI Semibold", 10))
    style.map("Accent.TButton",
              background=[("active", ACCENT_DARK), ("pressed", ACCENT_DARK)],
              foreground=[("disabled", MUTED)])
    style.configure("TButton", background=PANEL_ALT, foreground=TEXT,
                    borderwidth=1, relief="flat", padding=(10, 7))
    style.map("TButton", background=[("active", BORDER), ("pressed", BORDER)])
    style.configure("TEntry", fieldbackground=PANEL, foreground=TEXT,
                    insertcolor=TEXT, bordercolor=BORDER, padding=8)
    style.configure("TCombobox", fieldbackground=PANEL, background=PANEL_ALT,
                    foreground=TEXT, arrowcolor=ACCENT, padding=6)
    style.map("TCombobox", fieldbackground=[("readonly", PANEL)],
              foreground=[("readonly", TEXT)])
    style.configure("Treeview", background=PANEL, fieldbackground=PANEL,
                    foreground=TEXT, rowheight=29, borderwidth=0,
                    font=("Segoe UI", 9))
    style.configure("Treeview.Heading", background=PANEL_ALT, foreground=ACCENT,
                    font=("Segoe UI Semibold", 9), relief="flat", padding=8)
    style.map("Treeview", background=[("selected", "#344766")],
              foreground=[("selected", TEXT)])
    style.configure("TLabelframe", background=BG, foreground=ACCENT,
                    bordercolor=BORDER, relief="solid")
    style.configure("TLabelframe.Label", background=BG, foreground=ACCENT,
                    font=("Segoe UI Semibold", 9))
    style.configure("TProgressbar", troughcolor=PANEL_ALT, background=ACCENT,
                    bordercolor=PANEL_ALT, lightcolor=ACCENT, darkcolor=ACCENT)
    style.configure("TSeparator", background=BORDER)
