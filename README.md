# Convo History MCP

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-1.25+-green.svg)](https://modelcontextprotocol.io/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Render conversation history as beautiful, human-readable terminal output.**

An MCP server that fetches conversations directly from PostgreSQL and displays them as elegantly formatted dialogues. Built for the [Model Context Protocol](https://modelcontextprotocol.io/).

## Why Convo History MCP?

Ever stared at walls of JSON trying to debug a conversation? Yeah, us too.

Convo History MCP fetches conversation data straight from your database and renders it as clean, readable terminal output with proper alignment, text wrapping, and visual separation between user and assistant messages.

```
================================================================================
                     CONVERSATION: 26b2889f-1c8b-446e-ad85-917b378cfd80
================================================================================

                                                                          USER:
                    ------------------------------------------------------------
                                        What's the weather like in San Francisco?

--------------------------------------------------------------------------------
ASSISTANT:
--------------------------------------------------------------------------------
Based on current conditions, San Francisco is experiencing mild
temperatures around 65°F with partly cloudy skies. Perfect weather
for a walk along the Embarcadero!

================================================================================
                              END OF CONVERSATION
================================================================================
```

## Quick Start

```bash
claude mcp add --transport stdio convo-history --scope local \
  -e 'DATABASE_URL=${DATABASE_URL}' \
  -- docker run -i --rm -e DATABASE_URL ghcr.io/rreinold/convo-history-mcp:latest
```

Or add to your `~/.claude.json`:

```json
{
  "mcpServers": {
    "convo-history": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "DATABASE_URL",
        "ghcr.io/rreinold/convo-history-mcp:latest"
      ],
      "env": {
        "DATABASE_URL": "postgres://user:pass@host:5432/dbname"
      }
    }
  }
}
```

That's it. Claude Code will now have access to your conversation history.

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |

## Database Schema

The server expects the following tables:

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    chat_session_id VARCHAR UNIQUE,
    created_at TIMESTAMP
);

CREATE TABLE conversation_messages (
    id UUID PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id),
    user_input JSONB,
    assistant_response JSONB
);
```

**Message Format:**

```json
{
  "user_input": {"method": "chat", "message": "Hello!"},
  "assistant_response": {"answer": "Hi there! How can I help?"}
}
```

**Supported Message Types:**
- `chat` - Standard text messages
- `click` - User interactions (rendered as `[clicked: option_1]`)
- `output_list` - Option menus with emojis and descriptions
- `recommendation` - Summaries with cost estimates

## Features

| Feature | Description |
|---------|-------------|
| **Direct DB Access** | Fetches conversations via psql, no intermediate files |
| **Smart Text Wrapping** | Preserves paragraphs, wraps to 60 chars |
| **Visual Alignment** | User messages right-aligned, assistant left-aligned |
| **Rich Content** | Supports options, recommendations, costs |
| **MCP Native** | Built for Model Context Protocol |

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
