"""Stage 0 smoke test: one Messages API call, printing the reply, stop_reason and token usage.

Run with:  uv run python scripts/hello_claude.py
"""

import anthropic

from workpilot.config import get_settings


def main() -> None:
    settings = get_settings()
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key.get_secret_value())

    response = client.messages.create(
        model=settings.workpilot_model,
        max_tokens=1024,
        messages=[
            {"role": "user", "content": "In two sentences, what is an agentic loop?"},
        ],
    )

    # content is a list of blocks (thinking, text, tool_use, ...). Never assume content[0] is the text.
    for block in response.content:
        if block.type == "text":
            print(block.text)

    print("\n---")
    print(f"model:         {response.model}")
    print(f"stop_reason:   {response.stop_reason}")
    print(f"input tokens:  {response.usage.input_tokens}")
    print(f"output tokens: {response.usage.output_tokens}")
    print(f"block types:   {[block.type for block in response.content]}")


if __name__ == "__main__":
    main()
