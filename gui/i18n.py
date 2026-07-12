"""Simple internationalization (i18n) for English and Chinese."""

from PySide6.QtCore import QObject, Signal

_translations: dict[str, dict[str, str]] = {"en": {}, "zh": {}}
_current_lang = "en"


class I18n(QObject):
    language_changed = Signal(str)

    def set_language(self, lang: str):
        global _current_lang
        if lang not in _translations:
            return
        _current_lang = lang
        self.language_changed.emit(lang)

    @property
    def current_lang(self) -> str:
        return _current_lang


i18n = I18n()


def tr(key: str, **kwargs) -> str:
    """Translate a key. Falls back to the key when no translation exists."""
    text = _translations.get(_current_lang, {}).get(key, key)
    return text.format(**kwargs) if kwargs else text


def add_translations(key: str, en: str, zh: str):
    _translations["en"][key] = en
    _translations["zh"][key] = zh


# Application shell
add_translations("@window.title", "Subtitle Studio", "字幕工作室")
add_translations("@app.name", "Subtitle Studio", "字幕工作室")
add_translations("@app.eyebrow", "SUBTITLE STUDIO", "SUBTITLE STUDIO")
add_translations("@app.help", "Help", "帮助")
add_translations("@app.help_title", "Subtitle Studio Help", "字幕工作室帮助")
add_translations(
    "@app.help_body",
    "Separate bilingual subtitles, merge two monolingual files, or convert between SRT, ASS, SSA and VTT. Drag files into a card or click Browse.",
    "可以分离双语字幕、合并两个单语字幕，或在 SRT、ASS、SSA、VTT 之间转换格式。将文件拖入卡片，或点击“浏览”选择文件。",
)
add_translations("@status.ready", "Ready", "就绪")

# Navigation and page descriptions
add_translations("@tab.separate", "Separate", "字幕分离")
add_translations("@tab.merge", "Merge", "字幕合并")
add_translations("@tab.convert", "Convert", "格式转换")
add_translations("@page.separate.title", "Separate bilingual subtitles", "分离双语字幕")
add_translations(
    "@page.separate.desc",
    "Detect language order and split one bilingual subtitle into two independent files.",
    "识别字幕语言顺序，将双语字幕快速拆分为两个独立文件。",
)
add_translations("@page.merge.title", "Merge monolingual subtitles", "合并单语字幕")
add_translations(
    "@page.merge.desc",
    "Match entries by index and timestamp, then combine two files into one bilingual subtitle.",
    "按编号与时间轴匹配，将两个单语字幕合并为双语字幕。",
)
add_translations("@page.convert.title", "Convert subtitle formats", "转换字幕格式")
add_translations(
    "@page.convert.desc",
    "Convert between common subtitle formats while preserving compatible metadata.",
    "在常用字幕格式之间快速转换，并保留兼容的格式信息。",
)
add_translations("@lang.label", "Language:", "语言：")

# Separate panel
add_translations("@sep.import_title", "Import subtitle file", "导入字幕文件")
add_translations("@sep.drop_label", "Drop a bilingual subtitle here", "拖入双语字幕文件")
add_translations("@sep.no_file", "No file loaded", "尚未加载文件")
add_translations(
    "@sep.format_info",
    "{fmt} · {count} entries · line samples {lines}",
    "{fmt} · {count} 条字幕 · 行数示例 {lines}",
)
add_translations("@sep.language_title", "Automatic language detection", "自动识别语言")
add_translations(
    "@sep.language_desc",
    "Detect language order from the character patterns in each line.",
    "根据每行字符特征识别语言顺序。",
)
add_translations("@sep.auto_detect", "Auto-detect language assignment", "自动检测语言分配")
add_translations("@sep.line1_label", "First output", "第一个输出")
add_translations("@sep.line2_label", "Second output", "第二个输出")
add_translations("@sep.line1", "Line 1", "第 1 行")
add_translations("@sep.line2", "Line 2", "第 2 行")
add_translations("@sep.detected", "Detected:", "检测结果：")
add_translations("@sep.detected_title", "Detection result", "识别结果")
add_translations("@sep.detected_chip", "Line {line} · {lang}", "第 {line} 行 · {lang}")
add_translations("@sep.no_lang", "No language detected", "未检测到语言")
add_translations("@sep.output_format", "Output format", "输出格式")
add_translations("@sep.output_format_hint", "Keep the original format by default", "默认保持原始格式")
add_translations("@sep.same_as_input", "Same as input", "与输入相同")
add_translations("@sep.preview_title", "Subtitle preview", "字幕预览")
add_translations("@sep.preview_empty", "Load a file to preview its entries", "加载文件后显示字幕条目")
add_translations("@sep.preview_waiting", "Waiting", "等待文件")
add_translations(
    "@sep.preview_meta",
    "{count} entries · {missing} entries need attention",
    "共 {count} 条 · {missing} 条需要检查",
)
add_translations("@sep.preview_has_warnings", "{count} warnings", "{count} 条警告")
add_translations("@sep.preview_all_ok", "All entries normal", "所有条目正常")
add_translations("@sep.preview_error", "Load failed", "加载失败")
add_translations("@sep.lang1_out", "Language 1 output", "语言 1 输出")
add_translations("@sep.lang2_out", "Language 2 output", "语言 2 输出")
add_translations("@sep.lang1_placeholder", "Output path for language 1...", "语言 1 输出路径…")
add_translations("@sep.lang2_placeholder", "Output path for language 2...", "语言 2 输出路径…")
add_translations("@sep.btn_separate", "Start separation", "开始分离")
add_translations("@sep.save_as", "Save {suffix} as", "保存 {suffix}")
add_translations("@sep.missing_path_title", "Missing path", "缺少路径")
add_translations("@sep.missing_path_msg", "Please specify both output paths.", "请指定两条输出路径。")
add_translations("@sep.complete_title", "Separation complete", "分离完成")
add_translations("@sep.complete_msg", "Written:\n  {path1}\n  {path2}", "已写入：\n  {path1}\n  {path2}")
add_translations("@sep.warn_missing", "Warning: {n} entries had missing lines.", "警告：{n} 个条目缺少行。")
add_translations("@sep.status_done", "Separated: {path1}, {path2}", "已分离：{path1}，{path2}")

# Merge panel
add_translations("@merge.import_title", "Import two monolingual subtitles", "导入两个单语字幕")
add_translations(
    "@merge.import_desc",
    "Entries are matched automatically by index and timestamp.",
    "字幕条目会按编号与时间轴自动匹配。",
)
add_translations("@merge.primary_label", "Primary subtitle", "主字幕")
add_translations("@merge.secondary_label", "Secondary subtitle", "副字幕")
add_translations("@merge.primary_drop", "Drop primary file", "拖入主字幕")
add_translations("@merge.secondary_drop", "Drop secondary file", "拖入副字幕")
add_translations("@merge.no_file", "No file", "未选择文件")
add_translations("@merge.format_info", "{fmt} · {n} entries", "{fmt} · {n} 条字幕")
add_translations("@merge.options", "Merge options", "合并选项")
add_translations("@merge.ts_source", "Timestamp source", "时间轴来源")
add_translations("@merge.ts_primary", "Use primary timestamps", "使用主文件时间戳")
add_translations("@merge.ts_secondary", "Use secondary timestamps", "使用副文件时间戳")
add_translations("@merge.ts_primary_short", "Primary", "主字幕")
add_translations("@merge.ts_secondary_short", "Secondary", "副字幕")
add_translations("@merge.tolerance", "Allowed difference", "允许偏差")
add_translations("@merge.ordering", "Bilingual order", "双语顺序")
add_translations("@merge.order_pfirst", "Primary on top, secondary below", "主文件在上，副文件在下")
add_translations("@merge.order_sfirst", "Secondary on top, primary below", "副文件在上，主文件在下")
add_translations("@merge.order_pfirst_short", "Primary first", "主字幕在上")
add_translations("@merge.order_sfirst_short", "Secondary first", "副字幕在上")
add_translations("@merge.mismatch_label", "Count mismatch", "条目不一致")
add_translations("@merge.mismatch_pad", "Warn and pad with empty entries", "警告并用空条目填充")
add_translations("@merge.mismatch_trunc", "Truncate to the shorter file", "截断到较短文件")
add_translations("@merge.mismatch_pad_short", "Pad empty", "补齐空行")
add_translations("@merge.mismatch_trunc_short", "Truncate", "截断")
add_translations("@merge.header_label", "Style/header source", "样式来源")
add_translations("@merge.header_primary", "Primary", "主字幕")
add_translations("@merge.header_secondary", "Secondary", "副字幕")
add_translations("@merge.output_format", "Output format", "输出格式")
add_translations("@merge.same_as_primary", "Same as primary", "与主字幕相同")
add_translations("@merge.preview_title", "Merge preview", "合并预览")
add_translations("@merge.preview_empty", "Load both files to compare entries", "加载两个文件后显示匹配结果")
add_translations("@merge.preview_waiting", "Waiting", "等待文件")
add_translations(
    "@merge.preview_meta",
    "{count} entries · {conflicts} conflicts",
    "共 {count} 条 · {conflicts} 条冲突",
)
add_translations("@merge.preview_match_rate", "Match {rate}%", "匹配率 {rate}%")
add_translations("@merge.preview_all_ok", "Perfect match", "全部匹配")
add_translations("@merge.output", "Merged output", "合并后输出")
add_translations("@merge.output_placeholder", "Output path for merged file...", "合并文件输出路径…")
add_translations("@merge.btn_merge", "Start merge", "开始合并")
add_translations("@merge.save_as", "Save merged subtitle as", "保存合并字幕")
add_translations("@merge.missing_path_title", "Missing path", "缺少路径")
add_translations("@merge.missing_path_msg", "Please specify an output path.", "请指定输出路径。")
add_translations("@merge.complete_title", "Merge complete", "合并完成")
add_translations("@merge.complete_msg", "Merged file written to:\n{path}", "已写入合并文件：\n{path}")
add_translations("@merge.warnings", "Warnings: {n} conflict(s) found.\n", "警告：发现 {n} 处冲突。\n")
add_translations("@merge.conflict_entry", "  Entry {idx}: {ctype} - {detail}\n", "  条目 {idx}：{ctype} - {detail}\n")
add_translations("@merge.conflict_more", "  ... and {n} more.", "  …还有 {n} 处。")
add_translations("@merge.status_done", "Merged: {path} ({n} conflicts)", "已合并：{path}（{n} 处冲突）")

# Drop zone
add_translations("@drop.browse", "Browse", "选择文件")
add_translations("@drop.no_file", "No file selected...", "未选择文件…")
add_translations("@drop.hint", "Click the card or browse to select a file", "点击卡片或按钮选择文件")
add_translations("@drop.select_title", "Select subtitle file", "选择字幕文件")
add_translations(
    "@drop.file_filter",
    "Subtitle Files (*.srt *.ass *.ssa *.vtt);;All Files (*.*)",
    "字幕文件 (*.srt *.ass *.ssa *.vtt);;所有文件 (*.*)",
)

# Preview table
add_translations("@table.index", "#", "#")
add_translations("@table.time", "Time", "时间轴")
add_translations("@table.line1", "Line 1", "第 1 行")
add_translations("@table.line2", "Line 2", "第 2 行")
add_translations("@table.status", "Status", "状态")
add_translations("@table.primary", "Primary", "主字幕")
add_translations("@table.secondary", "Secondary", "副字幕")
add_translations("@table.ok", "Normal", "正常")
add_translations("@table.missing", "[missing]", "[缺失]")
add_translations("@table.missing_lines", "Missing lines", "缺少行")

# Errors
add_translations("@error.load", "Error: {msg}", "错误：{msg}")
add_translations("@error.no_lang", "No languages detected", "未检测到语言")

# Convert panel
add_translations("@convert.title", "Subtitle format conversion", "字幕格式转换")
add_translations(
    "@convert.description",
    "Convert between SRT, ASS, SSA and VTT while retaining encoding, newlines and compatible style data.",
    "在 SRT、ASS、SSA 和 VTT 之间快速转换，自动保留编码、换行符与兼容的样式信息。",
)
add_translations("@convert.import_title", "Import source file", "导入源文件")
add_translations("@convert.settings_title", "Conversion settings", "转换设置")
add_translations("@convert.drop_label", "Drop a subtitle file to convert", "拖入要转换的字幕文件")
add_translations("@convert.source_file", "Source file", "源文件")
add_translations("@convert.source_format", "Source format", "源格式")
add_translations("@convert.source_auto", "Detected automatically", "自动检测")
add_translations("@convert.target_format", "Target format", "目标格式")
add_translations("@convert.target_hint", "Choose the output container", "选择转换后的格式")
add_translations("@convert.output_path", "Output location", "输出位置")
add_translations("@convert.auto_output", "Automatic · same folder as source", "自动 · 与源文件同目录")
add_translations("@convert.choose_file", "Choose file", "选择文件")
add_translations("@convert.choose_output", "Choose location", "选择位置")
add_translations("@convert.start", "Start conversion", "开始转换")
add_translations("@convert.clear", "Clear", "清除")
add_translations("@convert.open_output_folder", "Open folder", "打开输出文件夹")
add_translations("@convert.status_title", "Status", "当前状态")
add_translations("@convert.status_waiting", "Waiting", "等待文件")
add_translations("@convert.status_ready", "Ready", "可转换")
add_translations("@convert.status_working", "Working", "转换中")
add_translations("@convert.status_done", "Done", "已完成")
add_translations("@convert.status_error", "Error", "失败")
add_translations("@convert.status.idle", "Drop or select a file to begin", "拖放或选择文件开始")
add_translations("@convert.status.detected", "Detected {fmt} · {count} entries", "检测到 {fmt} · {count} 条字幕")
add_translations("@convert.status.converting", "Converting...", "正在转换…")
add_translations("@convert.status.success", "Success: {msg}", "转换成功：{msg}")
add_translations("@convert.status.failed", "Failed: {msg}", "转换失败：{msg}")
add_translations("@convert.same_format", "Source and target formats are the same. The file will be saved as-is.", "源格式和目标格式相同，文件将按原格式保存。")
add_translations("@convert.output_title", "File converted", "转换完成")
add_translations("@convert.output_msg", "Output file:\n{path}", "输出文件：\n{path}")
