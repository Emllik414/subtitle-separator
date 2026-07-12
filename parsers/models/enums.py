from enum import Enum, auto


class SubtitleFormat(Enum):
    SRT = auto()
    ASS = auto()
    SSA = auto()
    VTT = auto()


class LanguageGroup(Enum):
    CJK = auto()
    LATIN = auto()
    CYRILLIC = auto()
    ARABIC = auto()
    KANA = auto()
    HANGUL = auto()
    THAI = auto()
    DEVANAGARI = auto()
    UNKNOWN = auto()
