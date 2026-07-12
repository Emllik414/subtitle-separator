from models.enums import LanguageGroup

# Unicode range definitions: (start, end) codepoint pairs
RANGES: dict[LanguageGroup, list[tuple[int, int]]] = {
    LanguageGroup.CJK: [
        (0x4E00, 0x9FFF),     # CJK Unified Ideographs
        (0x3400, 0x4DBF),     # CJK Extension A
        (0x20000, 0x2A6DF),   # CJK Extension B
        (0xF900, 0xFAFF),     # CJK Compatibility Ideographs
        (0x2F800, 0x2FA1F),   # CJK Compatibility Supplement
    ],
    LanguageGroup.KANA: [
        (0x3040, 0x309F),     # Hiragana
        (0x30A0, 0x30FF),     # Katakana
        (0xFF66, 0xFF9F),     # Halfwidth Katakana
    ],
    LanguageGroup.HANGUL: [
        (0xAC00, 0xD7AF),     # Hangul Syllables
        (0x1100, 0x11FF),     # Hangul Jamo
    ],
    LanguageGroup.LATIN: [
        (0x0041, 0x005A),     # A-Z
        (0x0061, 0x007A),     # a-z
        (0x00C0, 0x024F),     # Latin Extended A-B
        (0x1E00, 0x1EFF),     # Latin Extended Additional
    ],
    LanguageGroup.CYRILLIC: [
        (0x0400, 0x04FF),     # Cyrillic
        (0x0500, 0x052F),     # Cyrillic Supplement
    ],
    LanguageGroup.ARABIC: [
        (0x0600, 0x06FF),     # Arabic
        (0x0750, 0x077F),     # Arabic Supplement
        (0xFB50, 0xFDFF),     # Arabic Presentation Forms A
        (0xFE70, 0xFEFF),     # Arabic Presentation Forms B
    ],
    LanguageGroup.THAI: [
        (0x0E00, 0x0E7F),     # Thai
    ],
    LanguageGroup.DEVANAGARI: [
        (0x0900, 0x097F),     # Devanagari
    ],
}

PUNCTUATION_RANGES = [
    (0x2000, 0x206F),   # General Punctuation
    (0x3000, 0x303F),   # CJK Symbols and Punctuation
    (0xFF00, 0xFF0F),   # Halfwidth and Fullwidth Forms (punctuation)
    (0xFF1A, 0xFF1F),
    (0xFF3B, 0xFF40),
    (0xFF5B, 0xFF65),
]

DIGIT_RANGES = [
    (0x0030, 0x0039),   # 0-9
    (0xFF10, 0xFF19),   # Fullwidth 0-9
]


def _in_ranges(cp: int, ranges: list[tuple[int, int]]) -> bool:
    for lo, hi in ranges:
        if lo <= cp <= hi:
            return True
    return False


def classify_char(cp: int) -> LanguageGroup | None:
    """Return the LanguageGroup for a single codepoint, or None for punctuation/digits/whitespace."""
    if _in_ranges(cp, PUNCTUATION_RANGES):
        return None
    if _in_ranges(cp, DIGIT_RANGES):
        return None
    # Check script ranges
    for group, ranges in RANGES.items():
        if _in_ranges(cp, ranges):
            return group
    return None


def classify_line(line: str) -> LanguageGroup:
    """Classify a single text line into a LanguageGroup based on character majority."""
    from collections import Counter
    counts: dict[LanguageGroup, int] = {}
    for ch in line:
        if ch.isspace():
            continue
        g = classify_char(ord(ch))
        if g is not None:
            counts[g] = counts.get(g, 0) + 1
    total = sum(counts.values())
    if total == 0:
        return LanguageGroup.UNKNOWN
    best_group, best_count = max(counts.items(), key=lambda x: x[1])
    if best_count / total > 0.5:
        return best_group
    return LanguageGroup.UNKNOWN


def classify_lines(lines: list[str]) -> list[tuple[LanguageGroup, dict[LanguageGroup, int]]]:
    """Classify each line, returning (primary_group, full_counts) for each."""
    from collections import Counter
    results = []
    for line in lines:
        counts: dict[LanguageGroup, int] = {}
        for ch in line:
            if ch.isspace():
                continue
            g = classify_char(ord(ch))
            if g is not None:
                counts[g] = counts.get(g, 0) + 1
        total = sum(counts.values())
        if total == 0:
            results.append((LanguageGroup.UNKNOWN, {}))
            continue
        best_group = max(counts, key=counts.get)
        if counts[best_group] / total > 0.5:
            results.append((best_group, counts))
        else:
            results.append((LanguageGroup.UNKNOWN, counts))
    return results


def detect_language_assignment(entries) -> dict[int, LanguageGroup]:
    """
    Across all entries, determine the consensus LanguageGroup for each line index.
    Returns a dict mapping line_index -> LanguageGroup.
    """
    from collections import Counter
    tally: dict[int, Counter] = {}
    for entry in entries:
        classified = classify_lines(entry.lines)
        for i, (group, _) in enumerate(classified):
            if group != LanguageGroup.UNKNOWN:
                if i not in tally:
                    tally[i] = Counter()
                tally[i][group] += 1
    result = {}
    for idx, counter in tally.items():
        if counter:
            result[idx] = counter.most_common(1)[0][0]
    return result


# Human-readable names for language groups (bilingual)
LANGUAGE_GROUP_NAMES: dict[LanguageGroup, str] = {
    LanguageGroup.CJK: "Chinese / Japanese / Korean (CJK)",
    LanguageGroup.LATIN: "English / European (Latin)",
    LanguageGroup.CYRILLIC: "Russian / Slavic (Cyrillic)",
    LanguageGroup.ARABIC: "Arabic",
    LanguageGroup.KANA: "Japanese Kana",
    LanguageGroup.HANGUL: "Korean Hangul",
    LanguageGroup.THAI: "Thai",
    LanguageGroup.DEVANAGARI: "Hindi / Sanskrit (Devanagari)",
    LanguageGroup.UNKNOWN: "Unknown",
}

LANGUAGE_GROUP_NAMES_ZH: dict[LanguageGroup, str] = {
    LanguageGroup.CJK: "中文 / 日文 / 韩文 (CJK)",
    LanguageGroup.LATIN: "英文 / 欧洲语言 (拉丁)",
    LanguageGroup.CYRILLIC: "俄文 / 斯拉夫语 (西里尔)",
    LanguageGroup.ARABIC: "阿拉伯文",
    LanguageGroup.KANA: "日文假名",
    LanguageGroup.HANGUL: "韩文谚文",
    LanguageGroup.THAI: "泰文",
    LanguageGroup.DEVANAGARI: "印地语 / 梵文 (天城文)",
    LanguageGroup.UNKNOWN: "未知",
}
