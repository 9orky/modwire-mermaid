.PHONY: docs docs-check verify

docs:
	uv run python scripts/generate_docs.py
	uv run python scripts/generate_schemas.py
	uv run python scripts/generate_compatibility.py

docs-check:
	uv run python scripts/generate_docs.py --check
	uv run python scripts/generate_schemas.py --check
	uv run python scripts/generate_compatibility.py --check

verify: docs-check
	uv run ruff check .
	uv run pyright
	uv run pytest
