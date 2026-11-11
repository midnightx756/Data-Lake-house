import mimetypes
def describe_file(path):
    mime, _ = mimetypes.guess_type(str(path))
    return mime or "application/octet-stream"
