def normalize_extension(value):
    value=(value or "").strip().lower()
    if value and not value.startswith("."): value="."+value
    return value
