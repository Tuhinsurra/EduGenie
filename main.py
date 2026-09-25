"""
EduGenie Root Entrypoint
Allows running the server directly with:
    uvicorn main:app --reload
as described in Milestone 4 (Activity 4.1) of the project documentation.
"""
import sys
from pathlib import Path

# Ensure project root is in python path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
