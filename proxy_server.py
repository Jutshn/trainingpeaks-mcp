"""
Bindet den stdio-basierten TrainingPeaks-MCP-Server (tp-mcp) über einen
FastMCP-Proxy als HTTP-Server ein, damit er remote (z.B. auf Render.com)
erreichbar ist.
"""
import os
from fastmcp.client.transports import StdioTransport
from fastmcp.server import create_proxy
from starlette.requests import Request
from starlette.responses import PlainTextResponse

backend = StdioTransport(
    command="tp-mcp",
    args=["serve"],
    env=dict(os.environ),  # gibt TP_AUTH_COOKIE etc. an den Subprozess weiter
)
proxy = create_proxy(backend, name="trainingpeaks-proxy")

@proxy.custom_route("/", methods=["GET"])
async def health(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    proxy.run(transport="http", host="0.0.0.0", port=port)