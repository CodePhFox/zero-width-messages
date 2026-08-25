from __future__ import annotations

import unittest

from zero_width_messages import (
    CorruptHiddenMessageError,
    HiddenMessageError,
    NoHiddenMessageError,
    decode_message,
    encode_message,
    inspect_message,
    max_payload_bytes,
    utf16_length,
)
from zero_width_messages.codec import ZERO_WIDTH_ALPHABET


class CodecTests(unittest.TestCase):
    def test_round_trip_ascii_and_unicode(self) -> None:
        payload = "A secret with accents: ação — and emoji 🧪"
        encoded = encode_message("Nothing unusual here.", payload)
        self.assertEqual(decode_message(encoded), payload)

    def test_empty_payload_round_trips(self) -> None:
        encoded = encode_message("Visible", "")
        self.assertEqual(decode_message(encoded), "")

    def test_payload_may_contain_codec_characters_and_controls(self) -> None:
        payload = "".join(ZERO_WIDTH_ALPHABET) + "\n\t\0e\u0301 عربي 中文"
        encoded = encode_message("Visible", payload)
        self.assertEqual(decode_message(encoded), payload)

    def test_inspection_reports_visible_text_and_exact_sizes(self) -> None:
        encoded = encode_message("Hello 👋", "secret")
        info = inspect_message(encoded)
        self.assertEqual(info.visible_text, "Hello 👋")
        self.assertEqual(info.payload_utf8_bytes, 6)
        self.assertEqual(info.hidden_symbols, (12 + 6) * 4)
        self.assertEqual(info.utf16_units, utf16_length(encoded))

    def test_plain_text_is_not_mistaken_for_payload(self) -> None:
        with self.assertRaises(NoHiddenMessageError):
            decode_message("ordinary message")

    def test_checksum_detects_corruption(self) -> None:
        encoded = encode_message("Visible", "important payload")
        characters = list(encoded)
        characters[-1] = ZERO_WIDTH_ALPHABET[
            (ZERO_WIDTH_ALPHABET.index(characters[-1]) + 1) % 4
        ]
        with self.assertRaises(CorruptHiddenMessageError):
            decode_message("".join(characters))

    def test_decoder_tolerates_unrelated_leading_zero_width_symbol(self) -> None:
        encoded = ZERO_WIDTH_ALPHABET[0] + encode_message("Visible", "payload")
        self.assertEqual(decode_message(encoded), "payload")

    def test_carrier_must_be_visible_and_unambiguous(self) -> None:
        with self.assertRaises(ValueError):
            encode_message("", "payload")
        with self.assertRaises(ValueError):
            encode_message("\n\t", "payload")
        with self.assertRaises(ValueError):
            encode_message(f"bad{ZERO_WIDTH_ALPHABET[0]}carrier", "payload")

    def test_transport_limit_uses_utf16_units(self) -> None:
        self.assertEqual(utf16_length("A🧪"), 3)
        with self.assertRaisesRegex(ValueError, "limit is 60"):
            encode_message("🧪", "payload", limit=60)

    def test_capacity_accounts_for_frame_and_carrier(self) -> None:
        self.assertEqual(max_payload_bytes("A", 101), 13)
        payload = "x" * 13
        self.assertEqual(utf16_length(encode_message("A", payload, limit=101)), 101)

    def test_capacity_rejects_carriers_that_cannot_fit_an_empty_frame(self) -> None:
        with self.assertRaisesRegex(ValueError, "empty framed payload requires at least 48"):
            max_payload_bytes("Visible", 50)
        with self.assertRaisesRegex(ValueError, "cannot fit even an empty framed payload"):
            encode_message("Visible", "", limit=50)

    def test_capacity_validates_the_carrier(self) -> None:
        with self.assertRaisesRegex(ValueError, "visible text"):
            max_payload_bytes("", 2_000)
        with self.assertRaisesRegex(ValueError, "reserved zero-width"):
            max_payload_bytes(f"bad{ZERO_WIDTH_ALPHABET[0]}carrier", 2_000)

    def test_exact_limit_is_accepted_and_one_over_is_rejected(self) -> None:
        payload = "x" * max_payload_bytes("Ping", 2_000)
        encoded = encode_message("Ping", payload)
        self.assertEqual(utf16_length(encoded), 2_000)
        with self.assertRaises(ValueError):
            encode_message("Ping!", payload)

    def test_configurable_larger_transport_limit(self) -> None:
        payload = "x" * 600
        encoded = encode_message("Visible", payload, limit=4_000)
        self.assertEqual(decode_message(encoded), payload)

    def test_truncation_never_returns_partial_text(self) -> None:
        encoded = encode_message("Visible", "do not return this partially")
        for removed_symbols in (1, 2, 3, 4, 10):
            with self.assertRaises(HiddenMessageError):
                decode_message(encoded[:-removed_symbols])


if __name__ == "__main__":
    unittest.main()
