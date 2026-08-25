# Contributing

Contributions that improve correctness, portability, documentation, or safe testing are
welcome. Participation is governed by [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Development setup

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m unittest discover -s tests -v
```

The production package is intentionally dependency-free. The `dev` extra installs the
pinned repository linter:

```bash
ruff check src tests examples
python3 -m compileall -q src tests examples
```

## Pull requests

- Keep each change focused and explain why it is needed.
- Add tests for behavior changes and regressions.
- Update `docs/PROTOCOL.md` for any wire-format or compatibility change.
- Update `CHANGELOG.md` for user-visible changes.
- Preserve `LICENSE` and `NOTICE`.
- Do not include generated hidden messages, private payloads, account tokens, or platform
  automation.

Protocol changes need an explicit versioning plan. An incompatible change must not reuse
the `ZWM1` marker.

## Security reports

Do not open a public issue for a parser or packaging vulnerability. Follow
[SECURITY.md](SECURITY.md) and use GitHub private vulnerability reporting.

By submitting a contribution, you agree that it may be distributed under the Apache
License 2.0 used by this repository.
