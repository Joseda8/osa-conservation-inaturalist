# Agent Notes
Read the `README.md` to catch up with the project. In general keep changes simple and avoid overengineering.

## Development Constraints
- Do not execute project code unless the user explicitly asks for it.
- It is okay to inspect files and make small static checks when useful, but avoid commands like `src/main.py` without direct permission.
- Do not add unit or integration tests unless the user explicitly requests them.
- Keep temporary/cache files inside this project. Prefer `./tmp/` over `/tmp` or user/global cache directories.
- Avoid touching host-level filesystem locations unless the user explicitly asks.
- Use the existing virtual environment when needed: `.venv/`.
- Dependencies are listed in `requirements.txt`.
- Prefer iNaturalist API v2 through `pyinaturalist.v2` when the needed endpoint is available.

## Script Style
- Keep scripts short and direct.
- Keep argument definitions, print calls, and logging calls on one line.
- Define command-line argument defaults in `src/pipeline/constants.py` with a brief explanatory comment.
- Define operational constants in their corresponding package `constants.py` file with a brief explanatory comment; do not use magic numbers.
- Prefer clear, minimal code over helper layers or abstractions unless explicitly asked.
- For pyinaturalist cache/rate-limit files, configure `ClientSession` to use paths under `tmp/`.
- Avoid meaningless variable names like `f` or `data`; use descriptive names such as `output_file` or `observation_response`.
- Add concise Python docstrings for modules and functions. Doxygen-style tags such as `@file`, `@brief`, `@param`, and `@return` are welcome when they clarify intent.
- Add brief comments above constants to explain their purpose. Do not put these comments beside the code on the same line.
- Prefix private attributes and methods with `_`.
- Do not keep dead code or compatibility wrappers that are no longer used.
- Keep no more than one class per file. When adding a class, create a dedicated module for it.
- Keep the complete database baseline in `db/migrations/0001_initial_schema.sql`. Make subsequent schema changes through versioned SQL migrations in `db/migrations/` and preserve the ability to roll back to the baseline; do not create or change tables, indexes, or constraints with ad hoc runtime DDL.
