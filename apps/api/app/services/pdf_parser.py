import base64
from typing import Any

PROMPT = (
    "Extract the full text content of the attached PDF as GitHub-flavored Markdown. "
    "Preserve heading hierarchy (#, ##, ###), paragraphs, bullet and numbered lists, and "
    "inline emphasis. Do not summarize. Do not add commentary. Output Markdown only."
)


async def extract_markdown(
    pdf_bytes: bytes,
    filename: str,
    *,
    client: Any,
    model: str,
) -> str:
    encoded = base64.standard_b64encode(pdf_bytes).decode("ascii")
    response = await client.messages.create(
        model=model,
        max_tokens=8000,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": encoded,
                        },
                        "title": filename,
                    },
                    {"type": "text", "text": PROMPT},
                ],
            }
        ],
    )
    parts = [b.text for b in response.content if getattr(b, "type", None) == "text"]
    md = "\n".join(p for p in parts if p).strip()
    if not md:
        raise ValueError("Anthropic returned empty markdown")
    return md
