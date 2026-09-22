"""Node 2 — provisional schedule identity (§6.1). LLM, once, from the
opening pages only. Finalised later by Assemble (node 4), which sees
the whole document — supersession, dates and tax treatment often sit in
the general terms rather than the cover.
"""

from __future__ import annotations

from typing import Any

from .llm import structured_call
from .prompts import IDENTITY_SYSTEM_PROMPT, identity_user_prompt
from .schemas import ProvisionalIdentity

OPENING_PAGES_COUNT = 3


def provisional_identity(page_texts: dict[int, str], llm: Any) -> ProvisionalIdentity:
    opening_pages = "\n\n".join(
        f"[page {p}]\n{page_texts[p]}" for p in sorted(page_texts) if p <= OPENING_PAGES_COUNT and page_texts[p]
    )
    return structured_call(llm, ProvisionalIdentity, IDENTITY_SYSTEM_PROMPT, identity_user_prompt(opening_pages))
