#!/usr/bin/env python3.13
"""MCP Time Server with Bearer token authentication."""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

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
