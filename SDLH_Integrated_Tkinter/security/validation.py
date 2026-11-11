from pathlib import Path
def validate_folder(value):
    path=Path(value).expanduser().resolve()
    if not path.exists() or not path.is_dir(): raise ValueError("Select an existing folder.")
    return path
def validate_sql_readonly(sql):
    text=sql.strip().lower()
    if not text.startswith(("select","pragma","explain")): raise ValueError("Only SELECT/PRAGMA/EXPLAIN queries are allowed in the query console.")
    if ";" in text.rstrip(";"): raise ValueError("Multiple SQL statements are not allowed.")
    return sql
