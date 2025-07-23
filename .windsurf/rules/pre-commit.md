---
trigger: always_on
---

- After every code generation or code change, always run the pre-commit hook:

  ```bash
  uv run pre-commit run -a
  ```

- Fix all errors and warnings reported by pre-commit before committing or pushing changes.
- This ensures the codebase remains compliant with linting, formatting, and quality standards enforced by pre-commit hooks.
