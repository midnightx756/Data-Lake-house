from core.scanner import scan_folder
def run_pipeline(folder, max_files=None):
    return scan_folder(folder,max_files=max_files)
