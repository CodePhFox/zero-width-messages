# Zero-width message protocol

This document specifies protocol version `ZWM1`, implemented by
`zero_width_messages.codec`.

## Alphabet

Each zero-width character represents two bits. Alphabet order is part of the wire format.

| Bits | Unicode | Name |
|---|---|---|
| `00` | `U+200B` | ZERO WIDTH SPACE |
| `01` | `U+200C` | ZERO WIDTH NON-JOINER |
| `10` | `U+200D` | ZERO WIDTH JOINER |
| `11` | `U+2060` | WORD JOINER |

The symbols are invisible in normal rendering but remain real Unicode code points. A
platform may normalize, remove, expose, read aloud, or otherwise transform them.

## Binary frame

The encoder constructs this byte sequence before converting it to zero-width symbols:

| Offset | Size | Field | Encoding |
|---:|---:|---|---|
| `0` | `4` | magic/version | ASCII `ZWM1` |
| `4` | `4` | payload length | unsigned 32-bit, big-endian |
| `8` | variable | payload | UTF-8 bytes |
| `8 + length` | `4` | checksum | CRC32 of payload bytes, unsigned big-endian |

Frame overhead is 12 bytes. Because every byte becomes four zero-width symbols, the frame
costs 48 symbols before payload data.

## Symbol encoding

For each byte, encode bit pairs from most significant to least significant:

```text
bits 7–6, bits 5–4, bits 3–2, bits 1–0
```

For example, byte `0x1B` is binary `00011011`, so it maps to alphabet indices
`0, 1, 2, 3`, or `U+200B U+200C U+200D U+2060`.

The encoded frame is appended to the visible carrier. The carrier itself is not part of
the checksum and may be displayed or changed independently.

## Decoding

The decoder:

1. extracts only the four alphabet characters;
2. tries each of the four possible symbol alignments;
3. reconstructs bytes and searches for `ZWM1`;
4. reads the declared payload length;
5. validates the CRC32 checksum;
6. decodes the payload as UTF-8.

It returns a payload only after all validation succeeds. Truncation or modification within
the framed payload, and invalid UTF-8, fail with an explicit error. Unrelated zero-width
symbols outside the valid frame may be ignored while the decoder searches for `ZWM1`.

## Length accounting

Many messaging-platform limits are measured in UTF-16 code units:

```text
utf16_units = len(text.encode("utf-16-le")) / 2
```

Each character in the current alphabet is in the Basic Multilingual Plane and costs one
UTF-16 code unit. Many emoji and supplementary characters in a visible carrier cost two.

With a limit `L` and carrier cost `C`, maximum payload bytes are:

```text
max(0, floor((L - C) / 4) - 12)
```

## Security properties

`ZWM1` provides framing and accidental-corruption detection. It does not provide:

- encryption or confidentiality;
- message authentication;
- tamper resistance against an attacker;
- proof of authorship;
- platform-policy bypass.

CRC32 is intentionally used as an integrity check for transport experiments, not as a
cryptographic primitive.

## Compatibility policy

The byte layout and alphabet order remain stable for `ZWM1`. An incompatible revision
must use a new magic/version value and document its migration behavior. Decoders may add
support for new versions without changing the interpretation of existing `ZWM1` messages.
