"""
EduGenie Root Entrypoint
Configured for local Uvicorn development and Vercel Serverless deployment.
"""
import sys
import traceback
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

try:
    from app.main import app
except Exception:
    err_trace = traceback.format_exc()
    print("[EduGenie FATAL STARTUP ERROR]:", err_trace)
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse
    
    app = FastAPI(title="EduGenie Diagnostic Mode")
    
    @app.get("/")
    @app.get("/health")
    def startup_error():
        return HTMLResponse(
            f"<h2>EduGenie Diagnostic Error</h2><pre style='color:red;'>{err_trace}</pre>",
            status_code=200
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
