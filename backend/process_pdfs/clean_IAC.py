import os
import re

def clean_markdown(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    cleaned_lines = []

    for line in lines:
        original_line = line.rstrip()
        line_content = original_line.lstrip('#').strip()  # 去掉原有的所有#，只保留纯文本

        # 删除页眉
        if line_content == "Airport Authority Hong Kong Integrated Airport Centre Manual":
            continue

        new_line = None

        # 根据内容重新设置标题
        if re.match(r"(?i)^part\s+\d+", line_content):
            new_line = "# " + line_content
        elif re.match(r"(?i)^appendix\s*$", line_content):
            new_line = "# " + line_content
        elif re.match(r"(?i)^appendix\s+\d+", line_content):
            new_line = "## " + line_content
        elif re.match(r"^\d+\.\d+\s+", line_content):
            new_line = "## " + line_content

        # 如果匹配到了标题规则
        if new_line:
            cleaned_lines.append(new_line + "\n")
        else:
            cleaned_lines.append(line_content + "\n")  # 保持正文内容，且不带任何#开头

    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(cleaned_lines)

# 使用示例
input_file = "data/extracted/IAC/markdown/IAC Manual v9.md"
output_file = "data/extracted/IAC/cleaned_markdown/IAC Manual v9.md"

clean_markdown(input_file, output_file)
