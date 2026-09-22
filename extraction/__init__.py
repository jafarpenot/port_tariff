"""Tariff extraction pipeline (specs/EXTRACTION_SPEC.md).

Reads a port tariff PDF and proposes a rate schedule for tariffs/, for
human approval. Imports the schema, loader and validators from
`tariffs`; duplicates nothing (specs/EXTRACTION_SPEC.md §9). Optional
dependency group — `pip install -e .[extraction]`.
"""
