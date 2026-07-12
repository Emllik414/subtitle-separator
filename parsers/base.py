from abc import ABC, abstractmethod

from models.entry import SubtitleFile
from models.enums import SubtitleFormat


class AbstractParser(ABC):
    @staticmethod
    @abstractmethod
    def parse(raw_text: str) -> SubtitleFile:
        ...

    @staticmethod
    @abstractmethod
    def write(sub_file: SubtitleFile) -> str:
        ...


def detect_format(raw_text: str) -> SubtitleFormat:
    """Auto-detect subtitle format from content, tolerating common variants."""
    text = raw_text.lstrip("\ufeff \t\r\n")
    lower = text.lower()

    if lower.startswith("webvtt"):
        return SubtitleFormat.VTT

    if lower.startswith("[script info]") or "[events]" in lower:
        if "[v4+ styles]" in lower:
            return SubtitleFormat.ASS
        if "[v4 styles]" in lower:
            return SubtitleFormat.SSA
        return SubtitleFormat.ASS

    lines = [line.strip() for line in text.splitlines()[:12] if line.strip()]
    for index, line in enumerate(lines):
        if "-->" not in line:
            continue
        left, _, right = line.partition("-->")
        if _looks_like_srt_timestamp(left) and _looks_like_srt_timestamp(right):
            return SubtitleFormat.SRT
        if index > 3:
            break

    raise ValueError("Unable to detect subtitle format")


def _looks_like_srt_timestamp(value: str) -> bool:
    value = value.strip().split()[0] if value.strip() else ""
    parts = value.replace(".", ",").split(":")
    if len(parts) not in (2, 3):
        return False
    return "," in parts[-1] and all(part.replace(",", "").isdigit() for part in parts)


def get_parser(fmt: SubtitleFormat) -> type[AbstractParser]:
    from .srt import SrtParser
    from .ass import AssParser
    from .vtt import VttParser

    mapping = {
        SubtitleFormat.SRT: SrtParser,
        SubtitleFormat.ASS: AssParser,
        SubtitleFormat.SSA: AssParser,
        SubtitleFormat.VTT: VttParser,
    }
    return mapping[fmt]
