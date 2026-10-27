.PHONY: install run debug clean lint lint-strict

install:
	uv sync

run:
	uv run python3 -m src

debug:
	uv run python3 -m pdb -m src

clean:
	rm -rf __pycache__ .mypy_cache src/__pycache__ llm_sdk/llm_sdk/__pycache__ .pytest_cache

lint:
	uv run flake8 . --extend-exclude=llm_sdk
	uv run mypy . --warn-return-any --warn-unused-ignores \
				--ignore-missing-imports --disallow-untyped-defs \
				--check-untyped-defs --exclude llm_sdk

lint-strict:
	uv run flake8 .
	mypy . --strict

