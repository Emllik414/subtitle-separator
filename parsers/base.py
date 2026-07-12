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
    """Auto-detect subtitle format from file content."""
    text = raw_text.lstrip()
    if text.startswith("WEBVTT"):
        return SubtitleFormat.VTT
    if text.startswith("[Script Info]") or text.startswith("[Script info]"):
        # Distinguish ASS from SSA
        if "[V4+ Styles]" in text or "[V4+ Styles]" in text:
            return SubtitleFormat.ASS
        if "[V4 Styles]" in text:
            return SubtitleFormat.SSA
        return SubtitleFormat.ASS  # default to ASS
    # SRT: first non-blank line is a number
    first_line = text.split("\n")[0].strip()
    if first_line.isdigit():
        return SubtitleFormat.SRT
    raise ValueError("Unable to detect subtitle format")


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
