# SPDX-FileCopyrightText: 2026 CodePhFox
# SPDX-License-Identifier: Apache-2.0

"""Command-line interface for zero-width-messages."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from .codec import (
    DEFAULT_MESSAGE_LIMIT,
    HiddenMessageError,
    decode_message,
    encode_message,
    inspect_message,
    max_payload_bytes,
    utf16_length,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="zero-width-message",
        description="Hide and recover checksummed text inside an ordinary visible message.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    encode_parser = subparsers.add_parser("encode", help="create a hidden message")
    encode_parser.add_argument("carrier", help="visible message shown to readers")
    payload_group = encode_parser.add_mutually_exclusive_group()
    payload_group.add_argument("--payload", help="payload text (may be visible in shell history)")
    payload_group.add_argument("--payload-file", type=Path, help="read payload from a UTF-8 file")
    encode_parser.add_argument("-o", "--output", type=Path, help="write encoded text to a file")
    encode_parser.add_argument("--copy", action="store_true", help="copy encoded text to clipboard")
    encode_parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_MESSAGE_LIMIT,
        help="maximum UTF-16 units (default: 2000)",
    )

    decode_parser = subparsers.add_parser("decode", help="recover a hidden message")
    decode_parser.add_argument("input", nargs="?", type=Path, help="encoded UTF-8 file; stdin if omitted")
    decode_parser.add_argument("-o", "--output", type=Path, help="write decoded payload to a file")

    inspect_parser = subparsers.add_parser("inspect", help="show message sizes and decoded payload")
    inspect_parser.add_argument("input", nargs="?", type=Path, help="encoded UTF-8 file; stdin if omitted")
    inspect_parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")

    capacity_parser = subparsers.add_parser("capacity", help="calculate payload capacity")
    capacity_parser.add_argument("carrier", help="visible carrier text")
    capacity_parser.add_argument("--limit", type=int, default=DEFAULT_MESSAGE_LIMIT)
    capacity_parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "encode":
            return _run_encode(args)
        if args.command == "decode":
            return _run_decode(args)
        if args.command == "inspect":
            return _run_inspect(args)
        if args.command == "capacity":
            capacity = max_payload_bytes(args.carrier, args.limit)
            if args.json:
                print(
                    json.dumps(
                        {
                            "carrier": args.carrier,
                            "limit_utf16_units": args.limit,
                            "max_payload_utf8_bytes": capacity,
                        },
                        ensure_ascii=False,
                    )
                )
            else:
                print(f"{capacity} UTF-8 payload bytes")
            return 0
    except (OSError, UnicodeError, ValueError, HiddenMessageError) as error:
        parser.exit(1, f"error: {error}\n")
    return 2


def _run_encode(args: argparse.Namespace) -> int:
    if args.payload is not None:
        payload = args.payload
    elif args.payload_file is not None:
        payload = args.payload_file.read_text(encoding="utf-8")
    else:
        if sys.stdin.isatty():
            raise ValueError("provide --payload, --payload-file, or pipe the payload on stdin")
        payload = sys.stdin.read()

    encoded = encode_message(args.carrier, payload, limit=args.limit)
    if args.output is not None:
        args.output.write_text(encoded, encoding="utf-8")
    if args.copy:
        _copy_to_clipboard(encoded)
        print("Encoded message copied to the clipboard.", file=sys.stderr)
    if args.output is None and not args.copy:
        sys.stdout.write(encoded)
    print(
        f"visible={args.carrier!r} payload_bytes={len(payload.encode('utf-8'))} "
        f"utf16_units={utf16_length(encoded)}/{args.limit}",
        file=sys.stderr,
    )
    return 0


def _run_decode(args: argparse.Namespace) -> int:
    text = _read_input(args.input)
    payload = decode_message(text)
    if args.output is not None:
        args.output.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)
    return 0


def _run_inspect(args: argparse.Namespace) -> int:
    info = inspect_message(_read_input(args.input))
    if args.json:
        print(
            json.dumps(
                {
                    "visible_text": info.visible_text,
                    "hidden_symbols": info.hidden_symbols,
                    "utf16_units": info.utf16_units,
                    "payload_utf8_bytes": info.payload_utf8_bytes,
                    "checksum_valid": True,
                    "payload": info.payload,
                },
                ensure_ascii=False,
            )
        )
        return 0
    print(f"Visible text: {info.visible_text!r}")
    print(f"Hidden symbols: {info.hidden_symbols}")
    print(f"Message length: {info.utf16_units} UTF-16 units")
    print(f"Payload size: {info.payload_utf8_bytes} UTF-8 bytes")
    print("Checksum: OK")
    print("Payload:")
    sys.stdout.write(info.payload)
    if not info.payload.endswith("\n"):
        print()
    return 0


def _read_input(path: Path | None) -> str:
    if path is None:
        if sys.stdin.isatty():
            raise ValueError("provide an input file or pipe an encoded message on stdin")
        return sys.stdin.read()
    return path.read_text(encoding="utf-8")


def _copy_to_clipboard(text: str) -> None:
    candidates = (
        (["pbcopy"], "macOS"),
        (["wl-copy"], "Wayland"),
        (["xclip", "-selection", "clipboard"], "X11"),
        (["clip"], "Windows"),
    )
    for command, _platform in candidates:
        if shutil.which(command[0]):
            subprocess.run(command, input=text, text=True, check=True)
            return
    raise OSError("no supported clipboard command found (pbcopy, wl-copy, xclip, or clip)")
