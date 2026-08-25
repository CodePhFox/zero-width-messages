from __future__ import annotations

import unittest

from zero_width_messages.codec import (
    CHECKSUM,
    HEADER,
    MAGIC,
    ZERO_WIDTH_ALPHABET,
    _decode_digits,
    _encode_bytes,
)


class ProtocolTests(unittest.TestCase):
    def test_alphabet_order_is_stable(self) -> None:
        self.assertEqual(
            ZERO_WIDTH_ALPHABET,
            ("\u200b", "\u200c", "\u200d", "\u2060"),
        )

    def test_bit_pairs_are_encoded_most_significant_first(self) -> None:
        self.assertEqual(_encode_bytes(bytes([0x1B])), "".join(ZERO_WIDTH_ALPHABET))

    def test_documented_bit_pair_example_decodes(self) -> None:
        self.assertEqual(_decode_digits([0, 1, 2, 3]), bytes([0x1B]))

    def test_zwm1_golden_frame_for_single_ascii_byte(self) -> None:
        expected_frame = bytes.fromhex("5a574d310000000141d3d99e8b")
        self.assertEqual(HEADER.pack(MAGIC, 1) + b"A" + CHECKSUM.pack(0xD3D99E8B), expected_frame)
        expected_digits = [
            1, 1, 2, 2, 1, 1, 1, 3, 1, 0, 3, 1, 0, 3, 0, 1,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
            1, 0, 0, 1, 3, 1, 0, 3, 3, 1, 2, 1, 2, 1, 3, 2,
            2, 0, 2, 3,
        ]
        expected_encoded = "".join(ZERO_WIDTH_ALPHABET[index] for index in expected_digits)
        self.assertEqual(_encode_bytes(expected_frame), expected_encoded)
        self.assertEqual(_decode_digits(expected_digits), expected_frame)


if __name__ == "__main__":
    unittest.main()
