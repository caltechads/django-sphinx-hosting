# AGENTS.md

## Tooling Preflight (Required)

Before planning or implementation, show concise evidence of:

1. `graphify` for codebase exploration and knowledge exploration
2. At least one `code-index` call (search/find/symbol/summary as useful)
3. `context7` and/or `package-registry-mcp` when external library/package behavior, versioning, or package details matter

During Planning:

- Use `code-index` and `graphify` to find files and function calls

In an early progress update: tool names used + one line per result. If a tool is not relevant, say so in one line.

## Post-Implementation Quality Gate (Required)

After implementation edits [Important: Python code files only]:

1. `rtk .venv/bin/ruff` on touched files (or broader if needed)
2. `rtk .venv/bin/mypy` on touched files (or broader if needed)
3. `rtk make napoleon-gate`
4. Fix all reported problems before finishing

## Implementation Priority (Required)

Implement the correct product code directly. Do not add runtime patching, indirection, monkey-patching, startup hooks, or similar workarounds just to dodge doc-gate noise, baseline drift, or other documentation-tool friction.

1. Prefer 3rd-party open source packages that solve or can greatly assist the ADR/Spec/problem before building it ourselves

   a. Judge the 3rd-party package for code quality: commit cadence (is it abandoned); stars on github, other typical criteria
      and factor that into your decision.
   b. Use `context7` and `package-registry-mcp` to help you in searching and evaluating

2. Put the change in the correct source file, even when that file has noisy docs or baseline issues
3. Report quality-gate blockers separately, noting pre-existing or unrelated failures
4. Architecture and correctness beat avoiding documentation churn

## Project Structure (Mandatory)

1. The library itself: this is a standard Django app and lives in `./sphinx_hosting`
2. Documentation: the docs for the library live in `./doc/source`
3. Tests: the `pytest` tests for the library live in `./demo/tests`.  See "Testing" below.
4. Code organization: we follow standard Django conventions for all code
5. Demo app: since this is a library, to actually test it we need a full demo app. See "The Demo Application" below

## Testing

All tests are pytest tests.  All tests need a fully bootstrapped Django to run, so we run them inside the `demo` docker container.

```bash
cd sandbox
rtk make build
rtk make test
```

## AWS Interaction

Prefer botocraft models and managers. If botocraft lacks support, tell the user and stop: ask whether to extend botocraft or use straight boto3.

## Architecture (Required)

Prefer cohesive, human-comprehensible classes over loose function collections, even when mostly stateless.

- Model real workflow boundaries and stable domain concepts, not arbitrary namespaces
- Use constructor injection and explicit collaborators
- Keep methods and function bodies ≤ 60 lines
- **Single responsibility:** one clear job per service class; no god classes mixing many different concerns
- Split multi-concern workflows into named collaborators that map to human-understandable concepts
- Keep the public service a thin facade with a small entry-point API
- Put per-run orchestration and mutable run state in a dedicated execution/orchestrator class
- Prefer stateless collaborators; isolate per-run mutable state in one accumulator/orchestrator

Reference: `ExtractionOrchestrator` in `regis_inspector/services/orchestrator.py` (per-run orchestration + `RunStats` accumulator, driving stateless collaborators like `DdlExtractor`).

## The Demo Application

This is a Django library, and to fully test it we need a full Django stack.  This exists in ./sandbox and
runs as a Docker Compose stack

To work with the demo:

```shell
cd sandbox
make build  # This builds the demo container with our latest code
make dev  # This runs the docker compose stack
```

Containers in the compose stack:

- `demo`: the django-sphinx-hosting demo app.  This uses a Docker volume mount of ./sphinx_hosting to the appropriate place inside the container, and `gunicorn` is configured to reload when files change.
- `mysql`: the MySQL database the demo app uses
- `opensearch`: the Opensearch node that `demo` uses for documentation searches

On start of the demo compose stack, all pending Django migrations will be run.

## Documentation Contract (Required)

For all non-test Python code:

**Class docstrings:** describe the contract; include constructor `Args:` when constructor arguments exist.

**Function/method docstrings:** brief description plus only applicable sections:

- `Side Effects:` — real side effects only
- `Args:` — positional args only
- `Keyword Args:` — keyword args only
- `Raises:` — meaningful exceptions only
- `Returns:` or `Yields:` — when applicable

Do not add placeholder sections or empty/`None`-semantic sections.

**Napoleon `#:` comments** on class attributes, `__init__` instance attributes, and module-level globals.

Enforcement: `make napoleon-gate` (no new violations vs baseline); `make napoleon-gate-strict` when explicitly requested.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

When the user types `/graphify`, use the installed graphify skill or instructions before doing anything else.

Rules:

- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- Dirty graphify-out/ files are expected after hooks or incremental updates; dirty graph files are not a reason to skip graphify. Only skip graphify if the task is about stale or incorrect graph output, or the user explicitly says not to use it.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
