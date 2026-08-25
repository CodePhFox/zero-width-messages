# SPDX-FileCopyrightText: 2026 CodePhFox
# SPDX-License-Identifier: Apache-2.0

"""Public API for zero-width-messages."""

from .codec import (
    CorruptHiddenMessageError,
    HiddenMessageError,
    MessageInfo,
    NoHiddenMessageError,
    decode_message,
    encode_message,
    inspect_message,
    max_payload_bytes,
    utf16_length,
    visible_text,
)

__all__ = [
    "CorruptHiddenMessageError",
    "HiddenMessageError",
    "MessageInfo",
    "NoHiddenMessageError",
    "decode_message",
    "encode_message",
    "inspect_message",
    "max_payload_bytes",
    "utf16_length",
    "visible_text",
]

__version__ = "0.1.0"
