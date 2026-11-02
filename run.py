import sys
import os
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from genox.config import GENOX_PORT, GENOX_HOST

def run_server():
    import uvicorn
    print("\n" + "="*60)
    print("  🚀 GENOX AUTONOMOUS AGENT PLATFORM IS LAUNCHING")
    print(f"  🌐 Web Dashboard: http://{GENOX_HOST}:{GENOX_PORT}")
    print(f"  📁 Local Workspace: {ROOT_DIR}/workspace")
    print("="*60 + "\n")
    uvicorn.run("genox.server.app:app", host=GENOX_HOST, port=GENOX_PORT, reload=False)

def run_cli():
    from genox.cli import main
    main()

if __name__ == "__main__":
    if "--cli" in sys.argv:
        run_cli()
    else:
        run_server()
