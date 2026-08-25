# SPDX-FileCopyrightText: 2026 CodePhFox
# SPDX-License-Identifier: Apache-2.0

"""Encode UTF-8 text with zero-width Unicode characters."""

from __future__ import annotations

import struct
import unicodedata
import zlib
from dataclasses import dataclass

ZERO_WIDTH_ALPHABET = (
    "\u200b",  # ZERO WIDTH SPACE
    "\u200c",  # ZERO WIDTH NON-JOINER
    "\u200d",  # ZERO WIDTH JOINER
    "\u2060",  # WORD JOINER
)
ZERO_WIDTH_INDEX = {character: index for index, character in enumerate(ZERO_WIDTH_ALPHABET)}

MAGIC = b"ZWM1"
HEADER = struct.Struct(">4sI")
CHECKSUM = struct.Struct(">I")
FRAME_OVERHEAD_BYTES = HEADER.size + CHECKSUM.size
DEFAULT_MESSAGE_LIMIT = 2_000


class HiddenMessageError(ValueError):
    """Base exception for invalid or damaged hidden messages."""


class NoHiddenMessageError(HiddenMessageError):
    """Raised when no message created by this codec can be found."""


class CorruptHiddenMessageError(HiddenMessageError):
    """Raised when a framed message is present but fails validation."""


@dataclass(frozen=True)
class MessageInfo:
    visible_text: str
    hidden_symbols: int
    utf16_units: int
    payload: str
    payload_utf8_bytes: int


def utf16_length(text: str) -> int:
    """Return the number of UTF-16 code units used by many transport limits."""
    return len(text.encode("utf-16-le")) // 2


def visible_text(text: str) -> str:
    """Remove this codec's four zero-width symbols from a message."""
    return "".join(character for character in text if character not in ZERO_WIDTH_INDEX)


def max_payload_bytes(carrier: str, limit: int = DEFAULT_MESSAGE_LIMIT) -> int:
    """Return the largest UTF-8 payload, in bytes, that fits beside ``carrier``."""
    _validate_carrier(carrier)
    _validate_limit(limit)
    available_symbols = limit - utf16_length(carrier)
    minimum_symbols = FRAME_OVERHEAD_BYTES * 4
    if available_symbols < minimum_symbols:
        raise ValueError(
            f"carrier leaves {available_symbols} UTF-16 units; "
            f"an empty framed payload requires at least {minimum_symbols}"
        )
    return max(0, available_symbols // 4 - FRAME_OVERHEAD_BYTES)


def encode_message(
    carrier: str,
    payload: str,
    *,
    limit: int | None = DEFAULT_MESSAGE_LIMIT,
) -> str:
    """Append a framed, checksummed, zero-width payload to visible ``carrier`` text."""
    _validate_carrier(carrier)
    if limit is not None:
        _validate_limit(limit)

    payload_bytes = payload.encode("utf-8")
    frame = (
        HEADER.pack(MAGIC, len(payload_bytes))
        + payload_bytes
        + CHECKSUM.pack(zlib.crc32(payload_bytes))
    )
    encoded = carrier + _encode_bytes(frame)

    if limit is not None:
        encoded_length = utf16_length(encoded)
        if encoded_length > limit:
            try:
                capacity = max_payload_bytes(carrier, limit)
                capacity_message = f"This carrier can hold at most {capacity} payload bytes."
            except ValueError:
                capacity_message = "This carrier cannot fit even an empty framed payload."
            raise ValueError(
                f"encoded message uses {encoded_length} UTF-16 units; limit is {limit}. "
                f"{capacity_message}"
            )
    return encoded


def _validate_carrier(carrier: str) -> None:
    if not carrier:
        raise ValueError("carrier must contain visible text")
    if not any(
        not character.isspace()
        and unicodedata.category(character)[0] not in {"C", "M"}
        for character in carrier
    ):
        raise ValueError("carrier must contain at least one visible base character")
    if any(character in ZERO_WIDTH_INDEX for character in carrier):
        raise ValueError("carrier already contains a reserved zero-width character")


def _validate_limit(limit: int) -> None:
    if limit <= 0:
        raise ValueError("limit must be greater than zero")


def decode_message(text: str) -> str:
    """Find, validate, and decode a payload produced by :func:`encode_message`."""
    digits = [ZERO_WIDTH_INDEX[character] for character in text if character in ZERO_WIDTH_INDEX]
    minimum_symbols = FRAME_OVERHEAD_BYTES * 4
    if len(digits) < minimum_symbols:
        raise NoHiddenMessageError("no framed hidden message found")

    saw_magic = False
    for offset in range(4):
        raw = _decode_digits(digits[offset:])
        search_from = 0
        while True:
            frame_start = raw.find(MAGIC, search_from)
            if frame_start < 0:
                break
            saw_magic = True
            search_from = frame_start + 1

            header_end = frame_start + HEADER.size
            if len(raw) < header_end:
                continue
            _, payload_length = HEADER.unpack(raw[frame_start:header_end])
            payload_end = header_end + payload_length
            checksum_end = payload_end + CHECKSUM.size
            if checksum_end > len(raw):
                continue

            payload_bytes = raw[header_end:payload_end]
            expected_checksum = CHECKSUM.unpack(raw[payload_end:checksum_end])[0]
            if zlib.crc32(payload_bytes) != expected_checksum:
                continue
            try:
                return payload_bytes.decode("utf-8")
            except UnicodeDecodeError as error:
                raise CorruptHiddenMessageError("payload is not valid UTF-8") from error

    if saw_magic:
        raise CorruptHiddenMessageError("hidden message is truncated or failed its checksum")
    raise NoHiddenMessageError("no framed hidden message found")


def inspect_message(text: str) -> MessageInfo:
    """Return visible text, size information, and the validated payload."""
    payload = decode_message(text)
    return MessageInfo(
        visible_text=visible_text(text),
        hidden_symbols=sum(character in ZERO_WIDTH_INDEX for character in text),
        utf16_units=utf16_length(text),
        payload=payload,
        payload_utf8_bytes=len(payload.encode("utf-8")),
    )


def _encode_bytes(data: bytes) -> str:
    encoded: list[str] = []
    for byte in data:
        encoded.extend(
            (
                ZERO_WIDTH_ALPHABET[(byte >> 6) & 0b11],
                ZERO_WIDTH_ALPHABET[(byte >> 4) & 0b11],
                ZERO_WIDTH_ALPHABET[(byte >> 2) & 0b11],
                ZERO_WIDTH_ALPHABET[byte & 0b11],
            )
        )
    return "".join(encoded)


def _decode_digits(digits: list[int]) -> bytes:
    complete_length = len(digits) - (len(digits) % 4)
    return bytes(
        (digits[index] << 6)
        | (digits[index + 1] << 4)
        | (digits[index + 2] << 2)
        | digits[index + 3]
        for index in range(0, complete_length, 4)
    )
