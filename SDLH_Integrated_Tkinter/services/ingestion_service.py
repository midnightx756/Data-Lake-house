from security.validation import validate_folder
def scan_request(folder, job_manager):
    return job_manager.start_scan(validate_folder(folder))
