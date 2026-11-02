GOINFRE ?= $(HOME)/goinfre/CMM

export UV_CACHE_DIR ?= $(GOINFRE)/.uv_cache
export UV_PROJECT_ENVIRONMENT ?= $(GOINFRE)/.venv
export HF_HOME ?= $(GOINFRE)/.hf_cache
export UV_LINK_MODE ?= copy

.PHONY: install run debug clean lint lint-strict

install:
	uv sync

run:
	uv run python -m src

debug:
	uv run python -m pdb -m src

clean:
	rm -rf __pycache__ .mypy_cache src/__pycache__ llm_sdk/llm_sdk/__pycache__ .pytest_cache

lint:
	uv run flake8 src/
	uv run mypy src/ --warn-return-any --warn-unused-ignores \
				--ignore-missing-imports --disallow-untyped-defs \
				--check-untyped-defs --exclude llm_sdk

lint-strict:
	uv run flake8 src/
	uv run mypy --strict src/

