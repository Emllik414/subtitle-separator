"""Simple internationalization (i18n) for English and Chinese."""

from PySide6.QtCore import QObject, Signal

_translations: dict[str, dict[str, str]] = {
    "en": {},
    "zh": {},
}
_current_lang = "en"


class I18n(QObject):
    language_changed = Signal(str)

    def set_language(self, lang: str):
        global _current_lang
        _current_lang = lang
        self.language_changed.emit(lang)

    @property
    def current_lang(self) -> str:
        return _current_lang


i18n = I18n()


def tr(key: str, **kwargs) -> str:
    """Translate a key. Falls back to key if no translation found."""
    text = _translations.get(_current_lang, {}).get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    return text


def _add(lang: str, key: str, text: str):
    _translations[lang][key] = text


def add_translations(key: str, en: str, zh: str):
    _add("en", key, en)
    _add("zh", key, zh)


# ============================================================
# Main window
# ============================================================
add_translations("@window.title", "Bilingual Subtitle Tool - Separate & Merge", "双语字幕工具 - 分离与合并")
add_translations("@status.ready", "Ready", "就绪")

# ============================================================
# Tab names
# ============================================================
add_translations("@tab.separate", "Separate", "分离")
add_translations("@tab.merge", "Merge", "合并")

# ============================================================
# Manage bar
# ============================================================
add_translations("@lang.label", "Language:", "语言：")

# ============================================================
# Separate panel
# ============================================================
add_translations("@sep.drop_label", "Drop bilingual subtitle file here", "拖放双语字幕文件到此处")
add_translations("@sep.no_file", "No file loaded", "未加载文件")
add_translations("@sep.format_info", "Format: {fmt}  |  Entries: {count}  |  Lines per entry: {lines}", "格式：{fmt}  |  条目：{count}  |  每条目行数：{lines}")
add_translations("@sep.auto_detect", "Auto-detect language assignment", "自动检测语言分配")
add_translations("@sep.line1_label", "Line 1 language:", "第1行语言：")
add_translations("@sep.line2_label", "Line 2 language:", "第2行语言：")
add_translations("@sep.line1", "Line 1", "第1行")
add_translations("@sep.line2", "Line 2", "第2行")
add_translations("@sep.detected", "Detected:", "检测结果：")
add_translations("@sep.no_lang", "No languages detected", "未检测到语言")
add_translations("@sep.output_format", "Output format:", "输出格式：")
add_translations("@sep.same_as_input", "Same as input", "与输入相同")
add_translations("@sep.lang1_out", "Language 1 output:", "语言1输出：")
add_translations("@sep.lang2_out", "Language 2 output:", "语言2输出：")
add_translations("@sep.lang1_placeholder", "Output path for language 1...", "语言1输出路径...")
add_translations("@sep.lang2_placeholder", "Output path for language 2...", "语言2输出路径...")
add_translations("@sep.btn_separate", "Separate", "分离")
add_translations("@sep.missing_path_title", "Missing Path", "缺少路径")
add_translations("@sep.missing_path_msg", "Please specify both output paths.", "请指定两条输出路径。")
add_translations("@sep.complete_title", "Separation Complete", "分离完成")
add_translations("@sep.complete_msg", "Done. Written:\n  {path1}\n  {path2}", "完成。已写入：\n  {path1}\n  {path2}")
add_translations("@sep.warn_missing", "Warning: {n} entries had missing lines.", "警告：{n} 个条目缺少行。")
add_translations("@sep.status_done", "Separated: {path1}, {path2}", "已分离：{path1}, {path2}")

# ============================================================
# Merge panel
# ============================================================
add_translations("@merge.primary_label", "Primary File", "主文件")
add_translations("@merge.secondary_label", "Secondary File", "副文件")
add_translations("@merge.primary_drop", "Drop primary (first language) file", "拖放主文件（第一语言）")
add_translations("@merge.secondary_drop", "Drop secondary (second language) file", "拖放副文件（第二语言）")
add_translations("@merge.no_file", "No file", "未选择文件")
add_translations("@merge.format_info", "Format: {fmt}  |  Entries: {n}", "格式：{fmt}  |  条目：{n}")
add_translations("@merge.options", "Merge Options", "合并选项")
add_translations("@merge.ts_source", "Timestamp source:", "时间戳来源：")
add_translations("@merge.ts_primary", "Use primary timestamps", "使用主文件时间戳")
add_translations("@merge.ts_secondary", "Use secondary timestamps", "使用副文件时间戳")
add_translations("@merge.tolerance", "Timestamp tolerance (ms):", "时间戳容差 (毫秒)：")
add_translations("@merge.ordering", "Language ordering:", "语言排序：")
add_translations("@merge.order_pfirst", "Primary on top, secondary on bottom", "主文件在上，副文件在下")
add_translations("@merge.order_sfirst", "Secondary on top, primary on bottom", "副文件在上，主文件在下")
add_translations("@merge.mismatch_label", "On entry count mismatch:", "条目数不一致时：")
add_translations("@merge.mismatch_pad", "Warn and pad with empty entries", "警告并用空条目填充")
add_translations("@merge.mismatch_trunc", "Truncate to shorter file", "截断到较短文件")
add_translations("@merge.header_label", "Preserve header from:", "保留头部来源：")
add_translations("@merge.header_primary", "Primary", "主文件")
add_translations("@merge.header_secondary", "Secondary", "副文件")
add_translations("@merge.output_format", "Output format:", "输出格式：")
add_translations("@merge.same_as_primary", "Same as primary", "与主文件相同")
add_translations("@merge.output", "Output:", "输出：")
add_translations("@merge.output_placeholder", "Output path for merged file...", "合并文件输出路径...")
add_translations("@merge.btn_merge", "Merge", "合并")
add_translations("@merge.missing_path_title", "Missing Path", "缺少路径")
add_translations("@merge.missing_path_msg", "Please specify an output path.", "请指定输出路径。")
add_translations("@merge.complete_title", "Merge Complete", "合并完成")
add_translations("@merge.complete_msg", "Merged file written to:\n{path}", "已写入合并文件：\n{path}")
add_translations("@merge.warnings", "Warnings: {n} conflict(s) found.\n", "警告：发现 {n} 处冲突。\n")
add_translations("@merge.conflict_entry", "  Entry {idx}: {ctype} - {detail}\n", "  条目 {idx}：{ctype} - {detail}\n")
add_translations("@merge.conflict_more", "  ... and {n} more.", "  ... 还有 {n} 处。")
add_translations("@merge.status_done", "Merged: {path} ({n} conflicts)", "已合并：{path}（{n} 处冲突）")

# ============================================================
# Drop zone
# ============================================================
add_translations("@drop.browse", "Browse", "浏览")
add_translations("@drop.no_file", "No file selected...", "未选择文件...")
add_translations("@drop.hint", "or click Browse to select a file", "或点击浏览选择文件")
add_translations("@drop.select_title", "Select Subtitle File", "选择字幕文件")
add_translations("@drop.file_filter", "Subtitle Files (*.srt *.ass *.ssa *.vtt);;All Files (*.*)", "字幕文件 (*.srt *.ass *.ssa *.vtt);;所有文件 (*.*)")

# ============================================================
# Preview table headers
# ============================================================
add_translations("@table.index", "#", "#")
add_translations("@table.time", "Time", "时间")
add_translations("@table.line1", "Line 1", "第1行")
add_translations("@table.line2", "Line 2", "第2行")
add_translations("@table.status", "Status", "状态")
add_translations("@table.primary", "Primary", "主文件")
add_translations("@table.secondary", "Secondary", "副文件")
add_translations("@table.ok", "OK", "正常")
add_translations("@table.missing", "[missing]", "[缺失]")
add_translations("@table.missing_lines", "Missing lines", "缺少行")

# ============================================================
# Error messages
# ============================================================
add_translations("@error.load", "Error: {msg}", "错误：{msg}")
add_translations("@error.no_lang", "No languages detected", "未检测到语言")





# ============================================================
# Convert panel
# ============================================================
add_translations("@tab.convert", "Convert", "格式转换")
add_translations("@convert.title", "Format Convert", "格式转换")
add_translations("@convert.description", "Convert subtitle files between SRT, ASS, SSA, and VTT formats.", "在SRT、ASS、SSA、VTT格式之间转换字幕文件。")
add_translations("@convert.drop_label", "Drop subtitle file here", "拖放字幕文件到此处")
add_translations("@convert.source_file", "Source File", "源文件")
add_translations("@convert.source_format", "Detected format:", "检测到格式：")
add_translations("@convert.target_format", "Target format:", "目标格式：")
add_translations("@convert.output_path", "Output path:", "输出路径：")
add_translations("@convert.auto_output", "Auto (same folder)", "自动（同目录）")
add_translations("@convert.choose_file", "Choose File", "选择文件")
add_translations("@convert.choose_output", "Choose Output", "选择输出位置")
add_translations("@convert.start", "Start Convert", "开始转换")
add_translations("@convert.clear", "Clear", "清空")
add_translations("@convert.open_output_folder", "Open Output Folder", "打开输出目录")
add_translations("@convert.status.idle", "Idle - drop or select a file to begin", "就绪 - 拖放或选择文件开始")
add_translations("@convert.status.detected", "Detected: {fmt} - {count} entries", "检测到：{fmt} - {count}条字幕")
add_translations("@convert.status.converting", "Converting...", "正在转换...")
add_translations("@convert.status.success", "Success: {msg}", "转换成功：{msg}")
add_translations("@convert.status.failed", "Failed: {msg}", "转换失败：{msg}")
add_translations("@convert.same_format", "Source and target formats are the same. File will be saved as-is.", "源格式和目标格式相同，文件将按原格式保存。")
add_translations("@convert.output_title", "File Converted", "转换完成")
add_translations("@convert.output_msg", "Output file:\n{path}", "输出文件：\n{path}")
