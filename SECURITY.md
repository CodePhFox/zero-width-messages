# Security

This project performs local text transformation only. It does not need an account token,
webhook URL, API key, or network connection. Please do not add those credentials to an
issue, test fixture, example, or pull request.

Hidden payloads are neither encrypted, authenticated, nor confidential. Treat every
payload as public. A CRC32 checksum detects ordinary corruption; it is not a security
control and an attacker can replace it.

The supported security boundary is the parser and local CLI. Platform compatibility and
continued preservation of zero-width characters are not security guarantees.

If you find a vulnerability in the parser or packaging, report it privately through
GitHub's **Security → Report a vulnerability** feature rather than opening a public issue.

Supported release line: `0.1.x`. Security fixes are applied to the latest release only
until the project defines a longer-term support policy.
