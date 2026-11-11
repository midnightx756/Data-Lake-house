from concurrent.futures import ThreadPoolExecutor
from threading import Event, Lock
from database.connection import get_connection
from core.scanner import scan_folder
class JobManager:
    def __init__(self):
        self.executor=ThreadPoolExecutor(max_workers=1,thread_name_prefix="sdlh")
        self.lock=Lock(); self.cancel_event=Event(); self.last_result=None; self.status="idle"; self.message=""
    def start_scan(self, folder, callback=None):
        with self.lock:
            if self.status in {"queued","running"}: return False
            self.cancel_event=Event(); self.status="queued"; self.message="Queued"
            with get_connection() as conn:
                cur=conn.execute("INSERT INTO jobs(kind,target,status,message) VALUES('scan',?,'queued','Queued')",(str(folder),))
                self.job_id=cur.lastrowid
            self.executor.submit(self._run,folder,callback,self.job_id)
            return True
    def _run(self,folder,callback,job_id):
        with self.lock: self.status="running"; self.message="Scanning"
        with get_connection() as conn: conn.execute("UPDATE jobs SET status='running',started_at=CURRENT_TIMESTAMP WHERE job_id=?",(job_id,))
        try:
            result=scan_folder(folder,cancel_event=self.cancel_event,
                progress=lambda *args: callback(*args) if callback else None)
            self.last_result=result; self.status="cancelled" if self.cancel_event.is_set() else "completed"; self.message=self.status
            with get_connection() as conn:
                conn.execute("""UPDATE jobs SET status=?,finished_at=CURRENT_TIMESTAMP,scanned=?,inserted=?,
                  duplicates=?,errors=?,message=? WHERE job_id=?""",
                  (self.status,result["scanned"],result["inserted"],result["duplicates"],result["errors"],self.message,job_id))
        except Exception as exc:
            self.status="failed"; self.message=str(exc)
            with get_connection() as conn: conn.execute("UPDATE jobs SET status='failed',finished_at=CURRENT_TIMESTAMP,message=? WHERE job_id=?",(str(exc),job_id))
    def cancel(self): self.cancel_event.set()
