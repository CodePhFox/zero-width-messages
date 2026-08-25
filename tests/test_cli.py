from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from zero_width_messages import encode_message
from zero_width_messages.cli import main


class CliTests(unittest.TestCase):
    def test_encode_then_decode_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            encoded_path = root / "message.txt"
            decoded_path = root / "payload.txt"

            stderr = io.StringIO()
            with redirect_stderr(stderr):
                self.assertEqual(
                    main(
                        [
                            "encode",
                            "A normal message",
                            "--payload",
                            "surprise",
                            "--output",
                            str(encoded_path),
                        ]
                    ),
                    0,
                )
            self.assertIn("utf16_units=", stderr.getvalue())

            self.assertEqual(
                main(["decode", str(encoded_path), "--output", str(decoded_path)]),
                0,
            )
            self.assertEqual(decoded_path.read_text(encoding="utf-8"), "surprise")

    def test_capacity_command(self) -> None:
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            self.assertEqual(main(["capacity", "hello", "--limit", "100"]), 0)
        self.assertEqual(stdout.getvalue(), "11 UTF-8 payload bytes\n")

    def test_capacity_json_is_machine_readable(self) -> None:
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            self.assertEqual(main(["capacity", "hello", "--limit", "100", "--json"]), 0)
        self.assertEqual(
            json.loads(stdout.getvalue()),
            {
                "carrier": "hello",
                "limit_utf16_units": 100,
                "max_payload_utf8_bytes": 11,
            },
        )

    def test_inspect_reports_valid_checksum(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            message_path = Path(temporary_directory) / "message.txt"
            message_path.write_text(
                encode_message("Visible", "hidden"),
                encoding="utf-8",
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                self.assertEqual(main(["inspect", str(message_path)]), 0)
            self.assertIn("Checksum: OK\n", stdout.getvalue())

    def test_inspect_json_is_machine_readable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            message_path = Path(temporary_directory) / "message.txt"
            message_path.write_text(
                encode_message("Visible", "hidden"),
                encoding="utf-8",
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                self.assertEqual(main(["inspect", str(message_path), "--json"]), 0)
            self.assertEqual(
                json.loads(stdout.getvalue()),
                {
                    "visible_text": "Visible",
                    "hidden_symbols": 72,
                    "utf16_units": 79,
                    "payload_utf8_bytes": 6,
                    "checksum_valid": True,
                    "payload": "hidden",
                },
            )

    def test_copy_uses_available_clipboard_without_shell(self) -> None:
        with (
            patch("zero_width_messages.cli.shutil.which", return_value="/usr/bin/pbcopy"),
            patch("zero_width_messages.cli.subprocess.run") as run,
        ):
            self.assertEqual(
                main(["encode", "Visible", "--payload", "hidden", "--copy"]),
                0,
            )
        run.assert_called_once()
        command = run.call_args.args[0]
        self.assertEqual(command, ["pbcopy"])
        self.assertNotIn("shell", run.call_args.kwargs)
        self.assertTrue(run.call_args.kwargs["check"])


if __name__ == "__main__":
    unittest.main()
