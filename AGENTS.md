# AGENTS.md

These instructions apply to the entire repository. They are written for coding agents and
human contributors working on the public Zero Width Lab reference implementation.

## Start here

1. Read `README.md` for user-facing behavior and safety claims.
2. Read `docs/PROTOCOL.md` before changing the alphabet or binary frame.
3. Run the complete tests before and after any change.

```bash
python3 -m pip install -e '.[dev]'
python3 -m unittest discover -s tests -v
python3 -m compileall -q src tests examples
ruff check src tests examples
```

## Repository map

- `src/zero_width_messages/codec.py` — protocol, framing, encoding, decoding, sizing.
- `src/zero_width_messages/cli.py` — local command-line interface and clipboard output.
- `src/zero_width_messages/__init__.py` — intentionally supported public Python API.
- `pyproject.toml` — package metadata, Python compatibility, and CLI entry point.
- `tests/` — executable behavior and protocol invariants.
- `docs/PROTOCOL.md` — stable wire-format specification.
- `examples/` — small public API examples.
- `SECURITY.md` — security boundary and private reporting route.
- `NOTICE` and `LICENSE` — required redistribution notices.

## Protocol invariants

- Keep the magic bytes, byte order, alphabet order, and checksum layout compatible unless
  a new version is deliberately introduced.
- Every payload byte maps to exactly four symbols in most-significant-pair-first order.
- Length is the UTF-8 payload byte length, not a Python character count.
- Platform limits are measured in UTF-16 code units.
- Decoding must fail closed on truncation, checksum failure, or invalid UTF-8.
- A valid message must round-trip without changing its visible carrier.

Any protocol change requires tests, a specification update, and an explicit compatibility
note. Never silently reuse `ZWM1` for an incompatible frame.

The documented `0.1.x` JSON fields and command exit codes are also public compatibility
contracts. Change them only with tests, documentation, and a versioned compatibility note.

## Safety boundaries

- Do not add platform account tokens, webhooks, self-bot behavior, or message-sending
  automation.
- Do not describe the payload as encrypted, private, secure, or undetectable.
- Do not add moderation-evasion, credential-hiding, impersonation, or harassment examples.
- Do not commit encoded personal messages: their payloads remain recoverable.
- Keep the core library dependency-free unless a dependency has a concrete reviewed need.
- Never weaken corruption checks merely to return partial or plausible-looking text.

## Public identity boundary

Public authorship is `Zero Width Lab team at CodePhFox`. Do not add private names, personal
email addresses, local absolute paths, account exports, or credentials to files, examples,
commits, tags, issues, or release metadata.

Before publication, inspect tracked files and history for identity or secret leaks. Keep
the private-name blocklist outside this public repository. At a minimum, run the private
identity scanner plus:

```bash
gitleaks git --redact --no-banner
gitleaks dir . --redact --no-banner
git log --format=fuller --all
```

## Definition of done

- New and existing tests pass on supported Python versions.
- `ruff`, `compileall`, and `git diff --check` pass.
- Documentation matches actual behavior and does not overstate compatibility or security.
- The complete staged diff contains no private identity, secret, or encoded personal-message fixture.
- `LICENSE` and `NOTICE` remain present.
- User-visible changes are recorded in `CHANGELOG.md`.
