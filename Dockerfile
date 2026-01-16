FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

RUN apt-get update && \
    apt-get install -y postgresql-client && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY render_conversation.py .
COPY pyproject.toml .

RUN uv pip install --system mcp

# Environment variables:
#   DATABASE_URL: PostgreSQL connection string (required)
#   INPUT_COLUMN: Column name for user input (default: "input")
#   RESPONSE_COLUMN: Column name for assistant response (default: "response")

CMD ["python", "render_conversation.py"]

# Claude Code MCP config (~/.claude.json):
#
# {
#   "mcpServers": {
#     "conversation-renderer": {
#       "command": "docker",
#       "args": [
#         "run", "-i", "--rm",
#         "-e", "DATABASE_URL",
#         "-e", "INPUT_COLUMN=<MY_COLUMN_INPUT>",
#         "-e", "RESPONSE_COLUMN=<MY_COLUMN_RESPONSE>",
#         "conversation-renderer:latest"
#       ],
#       "env": {
#         "DATABASE_URL": "postgres://user:pass@host:5432/dbname"
#       }
#     }
#   }
# }
