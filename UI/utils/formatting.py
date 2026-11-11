def human_bytes(value):
    n=float(value or 0)
    for unit in ("B","KB","MB","GB","TB"):
        if n<1024 or unit=="TB": return f"{n:.1f} {unit}"
        n/=1024
