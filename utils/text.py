from __future__ import annotations

import codecs
import os
import tempfile
from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class PendingWrite:
    path: str
    text: str
    encoding: str = "utf-8"
    newline: str = "\r\n"
    add_bom: bool = False


def detect_bom_and_decode(raw_bytes: bytes) -> tuple[str, str]:
    """Return (decoded_text, encoding_name) with BOM handled."""
    if raw_bytes[:3] == codecs.BOM_UTF8:
        return raw_bytes[3:].decode("utf-8"), "utf-8-bom"
    if raw_bytes[:2] == codecs.BOM_UTF16_LE:
        return raw_bytes[2:].decode("utf-16-le"), "utf-16-le-bom"
    if raw_bytes[:2] == codecs.BOM_UTF16_BE:
        return raw_bytes[2:].decode("utf-16-be"), "utf-16-be-bom"

    for enc in ("utf-8", "gbk", "cp1252", "latin-1"):
        try:
            return raw_bytes.decode(enc), enc
        except UnicodeDecodeError:
            continue
    return raw_bytes.decode("utf-8", errors="replace"), "utf-8-replace"


def detect_newline(text: str) -> str:
    """Return the dominant newline convention."""
    crlf = text.count("\r\n")
    lf = text.count("\n") - crlf
    cr = text.count("\r") - crlf
    if crlf >= lf and crlf >= cr:
        return "\r\n"
    if cr > lf:
        return "\r"
    return "\n"


def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def denormalize_newlines(text: str, newline: str) -> str:
    if newline == "\n":
        return text
    return text.replace("\n", newline)


def read_subtitle_file(path: str) -> tuple[str, str, str]:
    """Read a subtitle and return normalized text, encoding and newline."""
    with open(path, "rb") as file:
        raw = file.read()
    text, encoding = detect_bom_and_decode(raw)
    newline = detect_newline(text)
    return normalize_newlines(text), encoding, newline


def _encode_text(text: str, encoding: str, add_bom: bool = False) -> bytes:
    """Encode text while preserving BOM-bearing source encodings."""
    normalized = encoding.lower().replace("_", "-")
    bom = b""

    if normalized in ("utf-8-bom", "utf-8-sig"):
        codec = "utf-8"
        bom = codecs.BOM_UTF8
    elif normalized in ("utf-16-le-bom", "utf-16le-bom"):
        codec = "utf-16-le"
        bom = codecs.BOM_UTF16_LE
    elif normalized in ("utf-16-be-bom", "utf-16be-bom"):
        codec = "utf-16-be"
        bom = codecs.BOM_UTF16_BE
    elif normalized == "utf-16-le":
        codec = "utf-16-le"
    elif normalized == "utf-16-be":
        codec = "utf-16-be"
    elif normalized == "utf-8-replace":
        codec = "utf-8"
    else:
        codec = encoding

    if add_bom:
        if codec == "utf-8":
            bom = codecs.BOM_UTF8
        elif codec == "utf-16-le":
            bom = codecs.BOM_UTF16_LE
        elif codec == "utf-16-be":
            bom = codecs.BOM_UTF16_BE

    return bom + text.encode(codec)


def _prepare_bytes(
    text: str,
    *,
    encoding: str = "utf-8",
    newline: str = "\r\n",
    add_bom: bool = False,
) -> bytes:
    return _encode_text(denormalize_newlines(text, newline), encoding, add_bom)


def write_subtitle_file(
    path: str,
    text: str,
    encoding: str = "utf-8",
    newline: str = "\r\n",
    add_bom: bool = False,
) -> None:
    """Atomically write subtitle text, preserving encoding and newlines."""
    write_subtitle_files_atomically([
        PendingWrite(path=path, text=text, encoding=encoding, newline=newline, add_bom=add_bom)
    ])


def write_subtitle_files_atomically(writes: Iterable[PendingWrite]) -> None:
    """Prepare every output first, then atomically replace destinations."""
    pending = list(writes)
    if not pending:
        return

    temp_paths: list[tuple[str, str]] = []
    try:
        for item in pending:
            destination = os.path.abspath(item.path)
            parent = os.path.dirname(destination) or os.getcwd()
            if not os.path.isdir(parent):
                raise FileNotFoundError(f"Output directory does not exist: {parent}")

            data = _prepare_bytes(
                item.text,
                encoding=item.encoding,
                newline=item.newline,
                add_bom=item.add_bom,
            )
            fd, temp_path = tempfile.mkstemp(prefix=".subtitle-", suffix=".tmp", dir=parent)
            try:
                with os.fdopen(fd, "wb") as file:
                    file.write(data)
                    file.flush()
                    os.fsync(file.fileno())
            except Exception:
                try:
                    os.close(fd)
                except OSError:
                    pass
                raise
            temp_paths.append((temp_path, destination))

        for temp_path, destination in temp_paths:
            os.replace(temp_path, destination)
    finally:
        for temp_path, _destination in temp_paths:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass


def canonical_path(path: str) -> str:
    return os.path.normcase(os.path.realpath(os.path.abspath(os.path.expanduser(path))))


def paths_equal(path_a: str, path_b: str) -> bool:
    if not path_a or not path_b:
        return False
    return canonical_path(path_a) == canonical_path(path_b)


def ensure_extension(path: str, extension: str) -> str:
    """Replace the current suffix with the requested extension."""
    extension = extension if extension.startswith(".") else f".{extension}"
    root, current = os.path.splitext(path)
    if current.lower() == extension.lower():
        return path
    return f"{root}{extension}" if current else f"{path}{extension}"


def strip_html_tags(text: str) -> str:
    import re
    return re.sub(r"<[^>]+>", "", text)


def strip_ass_tags(text: str) -> str:
    import re
    text = re.sub(r'\{[^}]*\}', '', text)
    text = re.sub(r'\{[^}]*$', '', text)
    return text.strip()
