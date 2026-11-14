from tkinter import ttk, messagebox
from ui.widgets import heading
from services.benchmark_service import run_benchmark
class BenchmarkFrame(ttk.Frame):
    def __init__(self,parent,app):
        super().__init__(parent); heading(self,"Benchmark Lab","Measures local SQLite metadata search; not a distributed-system benchmark.")
        ttk.Button(self,text="Run 100-query benchmark",command=self.run).pack(anchor="w",pady=8)
        self.result=ttk.Label(self,text="No benchmark run yet"); self.result.pack(anchor="w",pady=8)
    def run(self):
        try:
            r=run_benchmark()
            self.result.config(text=f'{r["iterations"]} iterations • {r["elapsed_seconds"]} sec • {r["avg_ms"]} ms/query • {r["records"]} assets')
        except Exception as e: messagebox.showerror("Benchmark failed",str(e))
