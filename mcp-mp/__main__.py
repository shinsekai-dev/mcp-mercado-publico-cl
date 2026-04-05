import os
import uvicorn
from interfaces.mcp.server import create_app

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=port)
