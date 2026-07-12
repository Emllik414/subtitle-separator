def detect_bom_and_decode(raw_bytes: bytes) -> tuple[str, str]:
    """Return (decoded_text, encoding_name) with BOM handled."""
    if raw_bytes[:3] == b"\xef\xbb\xbf":
        return raw_bytes[3:].decode("utf-8"), "utf-8-bom"
    if raw_bytes[:2] == b"\xff\xfe":
        return raw_bytes[2:].decode("utf-16-le"), "utf-16-le"
    if raw_bytes[:2] == b"\xfe\xff":
        return raw_bytes[2:].decode("utf-16-be"), "utf-16-be"
    # Try UTF-8 first, fall back to system locale
    for enc in ("utf-8", "gbk", "cp1252", "latin-1"):
        try:
            return raw_bytes.decode(enc), enc
        except UnicodeDecodeError:
            continue
    return raw_bytes.decode("utf-8", errors="replace"), "utf-8-replace"


def detect_newline(text: str) -> str:
    """Return the dominant newline convention: '\\r\\n', '\\n', or '\\r'."""
    crlf = text.count("\r\n")
    lf = text.count("\n") - crlf
    cr = text.count("\r") - crlf
    if crlf >= lf and crlf >= cr:
        return "\r\n"
    if cr > lf:
        return "\r"
    return "\n"


def normalize_newlines(text: str) -> str:
    """Normalize all newline conventions to \\n."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def denormalize_newlines(text: str, newline: str) -> str:
    """Convert \\n to the given newline convention."""
    if newline == "\n":
        return text
    return text.replace("\n", newline)


def read_subtitle_file(path: str) -> tuple[str, str, str]:
    """
    Read a subtitle file, handling encoding and newlines.
    Returns (normalized_text, encoding_name, detected_newline).
    """
    with open(path, "rb") as f:
        raw = f.read()
    text, encoding = detect_bom_and_decode(raw)
    nl = detect_newline(text)
    text = normalize_newlines(text)
    return text, encoding, nl


def write_subtitle_file(path: str, text: str, encoding: str = "utf-8",
                        newline: str = "\r\n", add_bom: bool = False) -> None:
    """Write normalized text to a subtitle file, restoring newlines and optionally adding BOM."""
    text = denormalize_newlines(text, newline)
    data = text.encode(encoding)
    if add_bom and encoding in ("utf-8", "utf-8-bom"):
        data = b"\xef\xbb\xbf" + data
    with open(path, "wb") as f:
        f.write(data)


def strip_html_tags(text: str) -> str:
    """Remove HTML-like tags from a text line (for language detection purposes)."""
    import re
    return re.sub(r"<[^>]+>", "", text)


def strip_ass_tags(text: str) -> str:
    """Remove ASS style override tags ({\\...}) from text."""
    import re
    # Remove complete override blocks: {\cmd1\cmd2...}
    text = re.sub(r'\{[^}]*\}', '', text)
    # Remove truncated trailing override: {\cmd... at end
    text = re.sub(r'\{[^}]*$', '', text)
    return text.strip()
