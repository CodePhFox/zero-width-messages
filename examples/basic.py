# SPDX-FileCopyrightText: 2026 CodePhFox
# SPDX-License-Identifier: Apache-2.0

"""Minimal public API example for Zero Width Messages."""

from zero_width_messages import decode_message, encode_message, inspect_message


def main() -> None:
    carrier = "Nothing unusual here 👀"
    payload = "You found the hidden message."

    encoded = encode_message(carrier, payload)
    info = inspect_message(encoded)

    print(f"Visible: {info.visible_text}")
    print(f"Hidden symbols: {info.hidden_symbols}")
    print(f"UTF-16 units: {info.utf16_units}")
    print(f"Decoded: {decode_message(encoded)}")


if __name__ == "__main__":
    main()
