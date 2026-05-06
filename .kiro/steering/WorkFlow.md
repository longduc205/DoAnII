---
inclusion: always
---

# Project Task Workflow

Execute every task through this pipeline, in order:

## Step 1 — Research First (ALWAYS)

Before writing any code or making any decisions, investigate the codebase:

1. Read relevant existing files in `app/`, `templates/`, `tests/` to understand current structure
2. Check related models in `app/models/`, services in `app/services/`, and routes in `app/routes/`
3. Review existing tests in `tests/` to understand expected behavior
4. Identify any patterns already established in the project before introducing new ones

**NEVER skip Step 1.** It prevents duplicate work, surfaces existing patterns, and avoids breaking dependencies.

## Step 2 — Plan Before Coding

After research, outline the plan clearly:

1. Identify which files need to be created or modified
2. Describe the approach in a few sentences before writing code
3. Check for potential side effects on other modules (crawler → scanner → detector → AI → DB)
4. Confirm the plan aligns with the project architecture:
   - `app/routes/` — Flask route handlers
   - `app/services/` — business logic (crawler, scanner, detector, AI)
   - `app/models/` — SQLAlchemy models
   - `app/utils/` — shared helpers
   - `templates/` — Jinja2 HTML templates

## Step 3 — Implement

Write clean, modular code following the project rules:

- Follow separation of concerns (UI / Scanner / AI / DB)
- Use meaningful variable and function names
- Avoid hardcoding values — use `app/config.py` for configuration
- Add comments only when necessary
- Keep code explainable for academic report purposes
- After editing, run relevant tests to verify correctness:

```bash
# Run all tests
python -m pytest tests/ -v

# Run a specific test file
python -m pytest tests/test_scanner.py -v
```

## Step 4 — Verify

Before considering a task done:

1. Run the test suite and confirm no regressions
2. Manually verify the feature works as expected (start Flask dev server if needed)
3. Check that database schema changes are reflected in `app/utils/db_init.py`
4. Ensure new routes are registered in `app/__init__.py`

```bash
# Start the development server manually
python -m flask run --debug
```

## Additional Rules

- **Language**: Always respond in **English** for code, comments, and documentation. If the user writes in **Vietnamese**, reply in Vietnamese with full diacritics.
- **No auto-commit or push**: Never run `git commit`, `git push`, or any git write commands automatically. Git operations are always manual and user-initiated.
- **No over-engineering**: Keep solutions simple and academic-appropriate. No complex ML models, no deep learning.
- **Modular first**: Prefer adding to existing service/utility files over creating new ones unless the separation is clearly justified.
- **Safe payloads only**: All vulnerability testing uses safe, non-destructive payloads for educational purposes.
