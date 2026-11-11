from core.backup import backup_database
def create_recovery_point(destination=None): return backup_database(destination)
