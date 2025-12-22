# MCP Time Server

Minimal MCP server that returns current time. Timezone configured on client side.

## Installation

```bash
python3.13 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Configuration

Create `config.json`:

```json
{
  "token": "your-secret-token",
  "port": 23386,
  "path": "/your-random-path"
}
```

## Running

```bash
.venv/bin/python server.py
```

## Client Configuration

### Claude Code CLI

```bash
claude mcp add time --transport sse \
  --url "https://DOMAIN/PATH/sse" \
  --header "Authorization: Bearer TOKEN" \
  --header "X-Timezone: Asia/Novokuznetsk"
```

### Claude Desktop

```json
{
  "mcpServers": {
    "time": {
      "command": "%APPDATA%\\npm\\mcp-remote.cmd",
      "args": [
        "https://DOMAIN/PATH/sse",
        "--header",
        "Authorization:Bearer ${MCP_TIME_TOKEN}",
        "--header",
        "X-Timezone:${MCP_TIME_TIMEZONE}"
      ],
      "env": {
        "MCP_TIME_TOKEN": "your-token",
        "MCP_TIME_TIMEZONE": "Asia/Novokuznetsk"
      }
    }
  }
}
```

## Xray Fallback

```json
"fallbacks": [
  {"path": "/PATH/sse", "dest": "127.0.0.1:PORT"},
  {"path": "/PATH/messages/", "dest": "127.0.0.1:PORT"}
]
```
