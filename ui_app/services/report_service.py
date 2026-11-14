from analytics.reporting import dashboard_metrics, extension_breakdown
def report(): return {"metrics":dashboard_metrics(),"extensions":extension_breakdown()}
