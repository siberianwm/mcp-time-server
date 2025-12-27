#!/usr/bin/env python3.13
"""MCP Time Server with Bearer token authentication."""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

# Monkey-patch SSE to add keepalive ping (prevents connection drops)
import sse_starlette.sse as sse_module
_original_init = sse_module.EventSourceResponse.__init__
def _patched_init(self, *args, **kwargs):
    kwargs.setdefault("ping", 15)  # Send ping every 15 seconds
    return _original_init(self, *args, **kwargs)
sse_module.EventSourceResponse.__init__ = _patched_init

# Monkey-patch MCP SSE to cleanup sessions on disconnect (fixes zombie sessions)
# See: https://github.com/modelcontextprotocol/python-sdk/issues/1227
import logging
from contextlib import asynccontextmanager
from mcp.server.sse import SseServerTransport

_original_connect_sse = SseServerTransport.connect_sse

@asynccontextmanager
async def _patched_connect_sse(self, scope, receive, send):
    async with _original_connect_sse(self, scope, receive, send) as streams:
        # Find session_id that was just created (last one added)
        session_id = list(self._read_stream_writers.keys())[-1] if self._read_stream_writers else None
        try:
            yield streams
        finally:
            # Cleanup session on disconnect
            if session_id and session_id in self._read_stream_writers:
                self._read_stream_writers.pop(session_id, None)
                logging.info(f"[MCP] Session {session_id} cleaned up on disconnect")

SseServerTransport.connect_sse = _patched_connect_sse

import uvicorn
from fastmcp import FastMCP, Context
from fastmcp.server.auth import StaticTokenVerifier
from fastmcp.server.http import create_sse_app
from fastmcp.server.dependencies import get_http_request

CONFIG_PATH = Path(__file__).parent / "config.json"


def load_config() -> dict:
    """Load configuration from JSON file."""
    with open(CONFIG_PATH) as f:
        return json.load(f)


config = load_config()

# Auth with static token
auth = StaticTokenVerifier(tokens={config["token"]: {"client_id": "mcp-client"}})

# Create MCP server
mcp = FastMCP("Time Server")


@mcp.tool
def get_time(ctx: Context) -> str:
    """Get current date and time in configured timezone."""
    request = get_http_request()
    timezone = request.headers.get("X-Timezone", "UTC")
    tz = ZoneInfo(timezone)
    now = datetime.now(tz)
    return now.strftime("%A, %d %B %Y, %H:%M:%S %Z")


# Create SSE app with custom paths under our prefix
app = create_sse_app(
    server=mcp,
    sse_path=f"{config['path']}/sse",
    message_path=f"{config['path']}/messages/",
    auth=auth,
)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=config["port"])
