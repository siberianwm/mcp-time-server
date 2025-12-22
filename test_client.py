#!/usr/bin/env python3.13
"""Test client for MCP Time Server."""

import asyncio
import json
from pathlib import Path

from fastmcp import Client
from fastmcp.client.transports import SSETransport

CONFIG_PATH = Path(__file__).parent / "config.json"

with open(CONFIG_PATH) as f:
    config = json.load(f)

url = f"https://visionguard-system.com{config['path']}/sse"
token = config["token"]


async def main():
    transport = SSETransport(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "X-Timezone": "Asia/Novokuznetsk",
        },
    )
    async with Client(transport) as client:
        # List tools
        tools = await client.list_tools()
        print("Available tools:", [t.name for t in tools])

        # Call get_time (timezone from header)
        result = await client.call_tool("get_time", {})
        print("Time:", result.data)


if __name__ == "__main__":
    asyncio.run(main())
