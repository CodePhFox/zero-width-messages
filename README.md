# Zero Width Messages

[![Tests](https://github.com/CodePhFox/zero-width-messages/actions/workflows/tests.yml/badge.svg)](https://github.com/CodePhFox/zero-width-messages/actions/workflows/tests.yml)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg)](https://www.python.org/)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

A dependency-free Python codec and command-line tool for placing a checksummed text
payload inside an ordinary visible message with four zero-width Unicode characters.

This is a **Zero Width Lab** project by the **CodePhFox team**. It was built for
transparent experiments, puzzles, scavenger hunts, and harmless messages between people
who understand how to reveal the hidden layer.

> [!IMPORTANT]
> This is steganography, not encryption. A recipient, platform, bot, moderation system,
> log processor, or Unicode inspector can recover or remove the payload. Never use it for
> passwords, confidential information, impersonation, harassment, or moderation evasion.

## Quick start

Python 3.10 or newer is required.

```bash
git clone https://github.com/CodePhFox/zero-width-messages.git
cd zero-width-messages
python3 -m venv .venv
.venv/bin/python -m pip install .
source .venv/bin/activate
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1` instead.

Encode a message and copy it to the clipboard:

```bash
zero-width-message encode "Nothing unusual here 👀" \
  --payload "You found the hidden message." \
  --copy
```

After sending it, copy the **delivered** message into a UTF-8 file and decode that copy:

```bash
zero-width-message decode delivered-message.txt
```

Inspect the visible carrier, payload size, UTF-16 length, checksum, and decoded payload:

```bash
zero-width-message inspect delivered-message.txt
```

Coding agents can request structured output:

```bash
zero-width-message inspect delivered-message.txt --json
zero-width-message capacity "Nothing unusual here 👀" --json
```

The JSON contract is stable for `0.1.x`:

- `inspect`: `visible_text` (string), `hidden_symbols` (integer), `utf16_units`
  (integer), `payload_utf8_bytes` (integer), `checksum_valid` (boolean), and `payload`
  (string).
- `capacity`: `carrier` (string), `limit_utf16_units` (integer), and
  `max_payload_utf8_bytes` (integer).

Successful commands exit with status `0`. Invalid input, capacity errors, damaged frames,
clipboard failures, and file errors exit with status `1` and write a human-readable
`error:` message to standard error. Argument-parser errors exit with status `2`.

Calculate payload capacity before encoding:

```bash
zero-width-message capacity "Nothing unusual here 👀"
```

## Why the delivered copy matters

The hidden layer passes through an encoder, clipboard, messaging platform, recipient,
and another clipboard operation. Any step may normalize or remove invisible characters.
A successful local round trip proves only the codec. Decoding the delivered copy tests
the real path.

Manual tests in August 2026 found that this four-character alphabet survived selected
Discord round trips. An informal iMessage test also worked, but has not yet been preserved
as independently reviewable release evidence. These are transport observations, not the
identity or limit of the project, and not compatibility guarantees. Clients and sanitizers
can change at any time.

## How it works

Every UTF-8 payload byte becomes four zero-width symbols, with each symbol carrying two
bits. A binary frame adds:

- a format marker and version;
- the payload byte length;
- the UTF-8 payload;
- a CRC32 integrity check.

The checksum detects ordinary truncation or modification within the framed payload. It
does not provide secrecy, authenticity, or protection from a deliberate attacker.

The CLI uses a conservative default budget of 2,000 UTF-16 code units. Change `--limit`
for the transport you are testing, or call the Python API with `limit=None` when you only
want the codec transformation. See [the protocol specification](docs/PROTOCOL.md) for the
exact byte layout and Unicode mapping.

## More input and output options

Use a file for multiline payloads or to keep a payload out of shell history:

```bash
zero-width-message encode "Just a normal message" \
  --payload-file payload.txt \
  --output encoded-message.txt
```

Pipe the payload on standard input:

```bash
printf 'surprise' | zero-width-message encode "Look closer" > encoded-message.txt
```

Use the Python API:

```python
from zero_width_messages import decode_message, encode_message

message = encode_message("Visible text", "hidden text")
assert decode_message(message) == "hidden text"
```

See [examples/basic.py](examples/basic.py) for a complete executable example.

## Practical limits

- Payload size is measured in UTF-8 bytes. Emoji and many non-ASCII characters use more
  capacity than their visible character count suggests.
- The carrier may not already contain any of the codec's four reserved characters.
- Clipboard support uses `pbcopy`, `wl-copy`, `xclip`, or `clip`, whichever is available.
- The tool creates text locally. It has no account-token support, message-sending
  automation, telemetry, or network requests.
- Compatibility must be re-tested against the specific client and transport you use.

## For coding agents

Start with [AGENTS.md](AGENTS.md), then read [docs/PROTOCOL.md](docs/PROTOCOL.md).
Those files define the repository map, invariants, safety boundaries, verification
commands, and compatibility rules. [llms.txt](llms.txt) provides a compact index for tools
that look for that convention.

The runtime package uses only the Python standard library. The optional development extra
adds the pinned linter used by CI:

```bash
python3 -m pip install -e '.[dev]'
python3 -m unittest discover -s tests -v
```

## Responsible use

Keep experiments consensual and easy to undo. Do not hide executable instructions,
credentials, threats, or content intended to bypass another person's or platform's
safety controls. This project deliberately does not automate user accounts or send
messages.

The project is not affiliated with Discord or Apple. Review the rules of any platform
before testing it there.

## Attribution and license

Licensed under the Apache License 2.0. Distributions and derivative works must preserve
the applicable attribution notices described in [NOTICE](NOTICE) and [LICENSE](LICENSE).

Suggested human-readable credit:

> Based on the Zero Width Lab zero-width message project by the CodePhFox team.

See [ATTRIBUTION.md](ATTRIBUTION.md) for details.

GitHub also exposes a ready-to-use citation through [CITATION.cff](CITATION.cff).
