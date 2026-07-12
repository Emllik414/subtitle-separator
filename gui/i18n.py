"""Simple internationalization (i18n) for English and Chinese."""

from PySide6.QtCore import QObject, Signal

_translations: dict[str, dict[str, str]] = {"en": {}, "zh": {}}
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
    text = _translations.get(_current_lang, {}).get(key, key)
    return text.format(**kwargs) if kwargs else text


def add_translations(key: str, en: str, zh: str):
    _translations["en"][key] = en
    _translations["zh"][key] = zh


# Main window and navigation
add_translations("@window.title", "Bilingual Subtitle Tool - Separate & Merge", "双语字幕工具 - 分离与合并")
add_translations("@app.short_title", "Subtitle Separator", "字幕分离器")
add_translations("@app.footer_note", "Apple-style desktop interface", "苹果风桌面界面")
add_translations("@app.help_title", "Subtitle Studio Help", "字幕工具帮助")
add_translations(
    "@app.help_text",
    "Import subtitle files by clicking or dragging them into a drop area. Output paths can be edited directly; double-click a path to choose a file location.",
    "点击或拖拽字幕文件到导入区域。输出路径可以直接编辑；双击路径可选择保存位置。",
)
add_translations("@status.ready", "Ready", "就绪")
add_translations("@tab.separate", "Separate", "分离")
add_translations("@tab.separate.full", "Subtitle Separate", "字幕分离")
add_translations("@tab.merge", "Merge", "合并")
add_translations("@tab.merge.full", "Subtitle Merge", "字幕合并")
add_translations("@tab.convert", "Format Convert", "格式转换")
add_translations("@lang.label", "Language:", "语言：")
add_translations("@page.separate.title", "Separate bilingual subtitles", "分离双语字幕")
add_translations("@page.separate.description", "Detect subtitle languages and split a bilingual file into two independent files.", "识别字幕语言，将双语字幕快速拆分为两个独立文件。")
add_translations("@page.merge.title", "Merge monolingual subtitles", "合并单语字幕")
add_translations("@page.merge.description", "Match by index and timeline, then merge two monolingual files into one bilingual subtitle.", "按编号与时间轴匹配，将两个单语字幕合并为双语字幕。")
add_translations("@page.convert.title", "Convert subtitle formats", "转换字幕格式")
add_translations("@page.convert.description", "Convert between common subtitle formats while preserving compatible format information.", "在常用字幕格式之间快速转换，并保留兼容的格式信息。")

# Separate panel — legacy/business messages
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

# Separate panel — preview layout copy
add_translations("@sep.preview_import_title", "Import subtitle file", "导入字幕文件")
add_translations("@sep.preview_drop_main", "Drop subtitle file", "拖入字幕文件")
add_translations("@sep.preview_auto_title", "Auto-detect languages", "自动识别语言")
add_translations("@sep.preview_auto_desc", "Detect the language order from each line's character features", "根据每行字符特征识别语言顺序")
add_translations("@sep.preview_detect_result", "Detection result", "识别结果")
add_translations("@sep.preview_output_format", "Output format", "输出格式")
add_translations("@sep.preview_output_hint", "Keep the original format by default", "默认保持原始格式")
add_translations("@sep.preview_title", "Subtitle preview", "字幕预览")
add_translations("@sep.preview_start", "Start separating", "开始分离")
add_translations("@sep.preview_file_meta", "{fmt} · {count} subtitles · {encoding}", "{fmt} · {count} 条字幕 · {encoding}")
add_translations("@sep.preview_loaded_status", "Loaded {count} subtitle entries", "已载入 {count} 条字幕")
add_translations("@sep.preview_load_failed", "Load failed", "载入失败")
add_translations("@sep.preview_line_language", "Line {line} · {language}", "第 {line} 行 · {language}")
add_translations("@sep.preview_output_name", "{language} output", "{language}输出")
add_translations("@sep.preview_empty_meta", "Import a subtitle file to preview it", "导入字幕文件后显示预览")
add_translations("@sep.preview_waiting", "Waiting", "等待文件")
add_translations("@sep.preview_auto_success", "Auto detection succeeded", "自动识别成功")
add_translations("@sep.preview_manual_mode", "Manual language order", "手动语言顺序")
add_translations("@sep.preview_meta", "Showing {count} entries · {mode}", "显示 {count} 条 · {mode}")
add_translations("@sep.preview_all_normal", "All entries normal", "所有条目正常")
add_translations("@sep.preview_missing_status", "{count} need review", "{count} 条需确认")
add_translations("@sep.language_one", "Language 1", "语言1")
add_translations("@sep.language_two", "Language 2", "语言2")
add_translations("@sep.preview_choose_output", "Choose {language} output", "选择 {language} 输出位置")

# Merge panel — legacy/business messages
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
add_translations("@merge.same_as_primary", "Same as primary", "与主字幕相同")
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

# Merge panel — preview layout copy
add_translations("@merge.preview_import_title", "Import two monolingual subtitles", "导入两个单语字幕")
add_translations("@merge.preview_import_desc", "Subtitle entries are matched automatically by index and timeline.", "字幕条目会按编号与时间轴自动匹配。")
add_translations("@merge.preview_primary_drop", "Primary subtitle", "主字幕")
add_translations("@merge.preview_secondary_drop", "Secondary subtitle", "副字幕")
add_translations("@merge.preview_options_title", "Merge options", "合并选项")
add_translations("@merge.preview_ts_title", "Timeline source", "时间轴来源")
add_translations("@merge.preview_primary", "Primary", "主字幕")
add_translations("@merge.preview_secondary", "Secondary", "副字幕")
add_translations("@merge.preview_tolerance_title", "Allowed offset", "允许偏差")
add_translations("@merge.preview_100ms", "100 ms", "100 ms")
add_translations("@merge.preview_custom", "Custom", "自定义")
add_translations("@merge.preview_order_title", "Bilingual order", "双语顺序")
add_translations("@merge.preview_primary_top", "Primary on top", "主字幕在上")
add_translations("@merge.preview_secondary_top", "Secondary on top", "副字幕在上")
add_translations("@merge.preview_mismatch_title", "Entry mismatch", "条目不一致")
add_translations("@merge.preview_pad", "Pad empty lines", "补齐空行")
add_translations("@merge.preview_truncate", "Truncate", "截断")
add_translations("@merge.preview_style_title", "Style source", "样式来源")
add_translations("@merge.preview_format_title", "Output format", "输出格式")
add_translations("@merge.preview_title", "Merge preview", "合并预览")
add_translations("@merge.preview_output", "Merged output", "合并后输出")
add_translations("@merge.preview_start", "Start merging", "开始合并")
add_translations("@merge.preview_compact_meta", "{fmt} · {count} entries", "{fmt} · {count} 条")
add_translations("@merge.preview_load_failed", "Subtitle load failed", "字幕载入失败")
add_translations("@merge.preview_ready_status", "Both subtitle files are ready", "两个字幕文件已就绪")
add_translations("@merge.preview_ready_title", "Primary and secondary subtitles are ready", "主字幕与副字幕已就绪")
add_translations("@merge.preview_ready_meta", "{primary} / {secondary} entries · timeline match {rate}%", "{primary} / {secondary} 条 · 时间轴匹配 {rate}%")
add_translations("@merge.preview_empty_meta", "Import two subtitle files to preview the merge", "导入两个字幕文件后显示合并预览")
add_translations("@merge.preview_waiting", "Waiting", "等待文件")
add_translations("@merge.preview_meta", "{count} entries · {conflicts} need review", "{count} 条 · {conflicts} 条需要确认")
add_translations("@merge.preview_rate", "Match rate {rate}%", "匹配率 {rate}%")
add_translations("@merge.preview_output_suffix", "bilingual", "双语")
add_translations("@merge.preview_choose_output", "Choose merged output", "选择合并文件输出位置")

# Drop zone
add_translations("@drop.browse", "Browse", "浏览")
add_translations("@drop.no_file", "No file selected...", "未选择文件...")
add_translations("@drop.hint", "or click the button below to select a file", "也可以点击下方按钮选择文件")
add_translations("@drop.select_title", "Select Subtitle File", "选择字幕文件")
add_translations("@drop.file_filter", "Subtitle Files (*.srt *.ass *.ssa *.vtt);;All Files (*.*)", "字幕文件 (*.srt *.ass *.ssa *.vtt);;所有文件 (*.*)")

# Preview table
add_translations("@table.index", "#", "#")
add_translations("@table.time", "Time", "时间")
add_translations("@table.timeline", "Timeline", "时间轴")
add_translations("@table.start_time", "Start time", "开始时间")
add_translations("@table.line1", "Line 1", "第1行")
add_translations("@table.line2", "Line 2", "第2行")
add_translations("@table.status", "Status", "状态")
add_translations("@table.primary", "Primary", "主字幕")
add_translations("@table.secondary", "Secondary", "副字幕")
add_translations("@table.ok", "Normal", "正常")
add_translations("@table.matched", "Matched", "已匹配")
add_translations("@table.missing", "[missing]", "[缺失]")
add_translations("@table.missing_lines", "Missing lines", "缺少行")

# Common errors
add_translations("@error.load", "Error: {msg}", "错误：{msg}")
add_translations("@error.no_lang", "No languages detected", "未检测到语言")

# Convert panel — legacy/business messages
add_translations("@convert.title", "Format Convert", "格式转换")
add_translations("@convert.description", "Convert subtitle files between SRT, ASS, SSA, and VTT formats.", "在SRT、ASS、SSA、VTT格式之间转换字幕文件。")
add_translations("@convert.drop_label", "Drop subtitle file here", "拖放字幕文件到此处")
add_translations("@convert.source_file", "Source File", "源文件")
add_translations("@convert.source_format", "Detected format:", "检测到格式：")
add_translations("@convert.target_format", "Target format:", "目标格式：")
add_translations("@convert.output_path", "Output path:", "输出路径：")
add_translations("@convert.auto_output", "Auto (same folder)", "自动（同目录）")
add_translations("@convert.choose_file", "Choose file", "选择文件")
add_translations("@convert.choose_output", "Choose Output", "选择输出位置")
add_translations("@convert.start", "Start converting", "开始转换")
add_translations("@convert.clear", "Clear", "清除")
add_translations("@convert.open_output_folder", "Open output folder", "打开输出文件夹")
add_translations("@convert.status.idle", "Idle - drop or select a file to begin", "就绪 - 拖放或选择文件开始")
add_translations("@convert.status.detected", "Detected: {fmt} - {count} entries", "检测到：{fmt} - {count}条字幕")
add_translations("@convert.status.converting", "Converting...", "正在转换...")
add_translations("@convert.status.success", "Success: {msg}", "转换成功：{msg}")
add_translations("@convert.status.failed", "Failed: {msg}", "转换失败：{msg}")
add_translations("@convert.same_format", "Source and target formats are the same. File will be saved as-is.", "源格式和目标格式相同，文件将按原格式保存。")
add_translations("@convert.output_title", "File Converted", "转换完成")
add_translations("@convert.output_msg", "Output file:\n{path}", "输出文件：\n{path}")

# Convert panel — preview layout copy
add_translations("@convert.preview_hero_title", "Subtitle format conversion", "字幕格式转换")
add_translations("@convert.preview_hero_desc", "Quickly convert between SRT, ASS, SSA and VTT while preserving encoding, line endings and compatible style information.", "在 SRT、ASS、SSA 和 VTT 之间快速转换，自动保留编码、换行符与可兼容的样式信息。")
add_translations("@convert.preview_import_title", "Import source file", "导入源文件")
add_translations("@convert.preview_drop_main", "Drop the subtitle file to convert", "拖入要转换的字幕文件")
add_translations("@convert.preview_settings_title", "Conversion settings", "转换设置")
add_translations("@convert.preview_source_format", "Source format", "源格式")
add_translations("@convert.preview_auto_detect", "Detected automatically", "自动检测")
add_translations("@convert.preview_target_format", "Target format", "目标格式")
add_translations("@convert.preview_target_desc", "Choose the converted format", "选择转换后的格式")
add_translations("@convert.preview_output_location", "Output location", "输出位置")
add_translations("@convert.preview_output_default", "Saved in the source folder by default", "默认保存在源文件目录")
add_translations("@convert.preview_output_name", "Output filename", "输出文件名")
add_translations("@convert.preview_choose_location", "Choose location", "选择位置")
add_translations("@convert.preview_loaded_meta", "{fmt} · {count} subtitles · {encoding}", "{fmt} · {count} 条字幕 · {encoding}")
add_translations("@convert.preview_source_value", "{fmt}\n{count} entries", "{fmt}\n{count} 条字幕")
add_translations("@convert.preview_no_output", "Waiting for source file", "等待源文件")
add_translations("@convert.preview_waiting", "Waiting", "等待文件")
add_translations("@convert.preview_ready", "Ready to convert", "可转换")
add_translations("@convert.preview_complete", "Converted", "已转换")
add_translations("@convert.preview_failed", "Failed", "转换失败")
add_translations("@convert.preview_load_failed", "Source file load failed", "源文件载入失败")
