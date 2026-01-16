"""Render conversation history as readable terminal output.

Usage:
    uv run render_conversation.py <chat_session_id>
    uv run render_conversation.py --file <path/to/conversation.jsonl>

Environment:
    DATABASE_URL - PostgreSQL connection string (required for database mode)
"""

import json
import os
import subprocess
import sys
import textwrap


def wrap_text(text: str, width: int) -> list[str]:
    """Wrap text to specified width, preserving newlines."""
    lines = []
    for paragraph in text.split("\n"):
        if paragraph.strip():
            wrapped = textwrap.wrap(paragraph, width=width) or [""]
            lines.extend(wrapped)
        else:
            lines.append("")
    return lines


def render_left(text: str, width: int, total_width: int) -> None:
    """Render text left-aligned (assistant)."""
    lines = wrap_text(text, width)
    print()
    print("-" * total_width)
    print("ASSISTANT:")
    print("-" * total_width)
    for line in lines:
        print(line)
    print()


def render_right(text: str, width: int, total_width: int) -> None:
    """Render text right-aligned (user)."""
    lines = wrap_text(text, width)
    print()
    print(" " * (total_width - len("USER:")) + "USER:")
    print(" " * (total_width - width) + "-" * width)
    for line in lines:
        padding = total_width - len(line)
        print(" " * padding + line)
    print()


def extract_user_message(mia_input: dict) -> str | None:
    """Extract readable message from user input."""
    if not mia_input:
        return None

    method = mia_input.get("method", "")
    message = mia_input.get("message", "")

    if method == "chat":
        return message
    elif method == "click":
        return f"[clicked: {message}]"
    else:
        return message if message else None


def extract_assistant_message(mia_response: dict) -> str | None:
    """Extract readable message from assistant response."""
    if not mia_response:
        return None

    parts = []

    answer = mia_response.get("answer")
    if answer:
        parts.append(answer.strip())

    output_list = mia_response.get("output_list")
    if output_list:
        options = []
        for item in output_list:
            label = item.get("label", "")
            emoji = item.get("emoji", "")
            desc = item.get("description", "")
            if emoji and emoji != "mia":
                option = f"  {emoji} {label}"
            else:
                option = f"  - {label}"
            if desc:
                option += f" ({desc})"
            options.append(option)
        if options:
            parts.append("Options:\n" + "\n".join(options))

    recommendation = mia_response.get("recommendation")
    if recommendation:
        summary = recommendation.get("summary", "")
        cost = recommendation.get("total_estimated_cost", "")
        if summary or cost:
            rec_text = ""
            if summary:
                rec_text += f"Summary: {summary}"
            if cost:
                rec_text += f"\nEstimated Cost: {cost}"
            parts.append(rec_text.strip())

    return "\n\n".join(parts) if parts else None


def fetch_from_database(chat_session_id: str) -> list[str]:
    """Fetch conversation from PostgreSQL using psql."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("Error: DATABASE_URL environment variable is required", file=sys.stderr)
        sys.exit(1)

    query = f"""
        SELECT json_build_object('mia_input', mia_input, 'mia_response', mia_response)
        FROM conversation_messages
        WHERE conversation_id = (
            SELECT id FROM conversations
            WHERE chat_session_id = '{chat_session_id}'
            ORDER BY created_at ASC
        )
    """

    result = subprocess.run(
        ["psql", database_url, "-t", "-A", "-c", query],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"Error running psql: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    return [line for line in result.stdout.strip().split("\n") if line]


def render_conversation(lines: list[str], title: str) -> None:
    """Render conversation lines to terminal."""
    total_width = 80
    column_width = 60

    print("=" * total_width)
    print(f"CONVERSATION: {title}".center(total_width))
    print("=" * total_width)

    for line in lines:
        if not line.strip():
            continue

        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue

        mia_input = entry.get("mia_input")
        mia_response = entry.get("mia_response")

        user_msg = extract_user_message(mia_input)
        if user_msg:
            render_right(user_msg, column_width, total_width)

        assistant_msg = extract_assistant_message(mia_response)
        if assistant_msg:
            render_left(assistant_msg, column_width, total_width)

    print("=" * total_width)
    print("END OF CONVERSATION".center(total_width))
    print("=" * total_width)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage:", file=sys.stderr)
        print("  uv run render_conversation.py <chat_session_id>", file=sys.stderr)
        print("  uv run render_conversation.py --file <path.jsonl>", file=sys.stderr)
        sys.exit(1)

    if sys.argv[1] == "--file":
        if len(sys.argv) < 3:
            print("Error: --file requires a path argument", file=sys.stderr)
            sys.exit(1)
        filepath = sys.argv[2]
        with open(filepath) as f:
            lines = f.readlines()
        render_conversation(lines, filepath)
    else:
        chat_session_id = sys.argv[1]
        lines = fetch_from_database(chat_session_id)
        render_conversation(lines, chat_session_id)


if __name__ == "__main__":
    main()
