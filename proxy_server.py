"""
Bindet den stdio-basierten TrainingPeaks-MCP-Server (tp-mcp) über einen
FastMCP-Proxy als HTTP-Server ein, damit er remote (z.B. auf Render.com)
erreichbar ist.
"""

import os

from fastmcp import FastMCP
from fastmcp.client.transports import StdioTransport

backend = StdioTransport(
    command="tp-mcp",
    args=["serve"],
    env=dict(os.environ),  # gibt TP_AUTH_COOKIE etc. an den Subprozess weiter
)

proxy = FastMCP.as_proxy(backend, name="trainingpeaks-proxy")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    proxy.run(transport="http", host="0.0.0.0", port=port)
