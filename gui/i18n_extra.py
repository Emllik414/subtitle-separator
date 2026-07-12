"""Additional copy for validation, safety, and large-preview states."""

from gui.i18n import add_translations


add_translations(
    "@error.no_entries",
    "No valid subtitle entries were found in this file.",
    "文件中没有找到有效的字幕条目。",
)
add_translations(
    "@error.output_path_title",
    "Invalid output path",
    "输出路径无效",
)
add_translations(
    "@error.outputs_must_differ",
    "The two output files must use different paths.",
    "两个输出文件不能使用同一个路径。",
)
add_translations(
    "@error.output_overwrites_source",
    "The output file cannot overwrite an imported source file.",
    "输出文件不能覆盖已导入的源字幕文件。",
)
add_translations(
    "@error.write_title",
    "Unable to write output",
    "无法写入输出文件",
)
add_translations(
    "@error.write_failed",
    "Writing failed: {msg}",
    "写入失败：{msg}",
)
add_translations(
    "@error.open_folder_failed",
    "Unable to open the output folder: {msg}",
    "无法打开输出文件夹：{msg}",
)
add_translations(
    "@table.preview_limited_short",
    "previewing first {limit}",
    "仅预览前 {limit} 条",
)
add_translations(
    "@convert.preview_path_conflict",
    "Choose another output path",
    "请选择其他输出路径",
)
