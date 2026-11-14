from tkinter import ttk
def heading(parent, text, subtitle=None):
    ttk.Label(parent, text=text, style="Title.TLabel").pack(anchor="w", pady=(0, 4))
    if subtitle:
        ttk.Label(parent, text=subtitle, style="Subtitle.TLabel").pack(anchor="w", pady=(0, 12))
def tree(parent, columns, headings):
    view = ttk.Treeview(parent, columns=columns, show="headings")
    for col, title in zip(columns, headings):
        view.heading(col, text=title)
        view.column(col, width=140, anchor="w")
    view.pack(fill="both", expand=True, pady=8)
    return view
def fill_tree(view, rows, columns):
    view.delete(*view.get_children())
    for row in rows:
        view.insert("", "end", values=tuple(row.get(c, "") for c in columns))
