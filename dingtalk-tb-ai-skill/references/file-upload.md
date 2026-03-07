# 文件上传

使用 Teambition API 上传文件到对象存储（OSS），获取文件 Token 用于任务评论、自定义字段等场景。

## 快速开始

```bash
# 上传文件到任务
uv run scripts/simple-upload.py \
  --file-path '/path/to/file.jpg' \
  --scope 'task:69a252ad3e86c360f083e06c' \
  --category 'attachment'
```

## 参数说明

| 参数 | 必填 | 说明 | 示例 |
|------|------|------|------|
| `--file-path` | ✅ | 文件路径 | `/path/to/file.jpg` |
| `--scope` | ✅ | 业务范围 | `task:{taskId}` 或 `project:{projectId}` |
| `--category` | ✅ | 文件类别 | `attachment`（最常用）、`rich-text`、`work` |

## 使用示例

### 示例 1：上传图片到任务

```bash
uv run scripts/simple-upload.py \
  --file-path '/Users/username/Pictures/screenshot.png' \
  --scope 'task:69a252ad3e86c360f083e06c' \
  --category 'attachment'
```

### 示例 2：上传文档到项目

```bash
uv run scripts/simple-upload.py \
  --file-path '/Users/username/Documents/report.pdf' \
  --scope 'project:69a03cd9cd778ff7d8974858' \
  --category 'attachment'
```

### 示例 3：上传文件并创建任务评论

```python
#!/usr/bin/env python3
import subprocess
import json

TASK_ID = "69a252ad3e86c360f083e06c"
FILE_PATH = "/path/to/report.pdf"

# 上传文件
result = subprocess.run(
    ["uv", "run", "scripts/simple-upload.py",
     "--file-path", FILE_PATH,
     "--scope", f"task:{TASK_ID}",
     "--category", "attachment"],
    capture_output=True,
    text=True
)

# 提取文件 Token
file_token = None
for line in result.stdout.split('\n'):
    if 'Token:' in line:
        file_token = line.split('Token:')[1].strip()
        break

# 创建任务评论
comment_data = {
    "content": "任务完成了，详见附件",
    "fileTokens": [file_token]
}

subprocess.run(
    ["uv", "run", "scripts/call-user-api.py", "POST",
     f"v3/task/{TASK_ID}/comment",
     json.dumps(comment_data)],
    capture_output=True,
    text=True
)
```

### 示例 4：批量上传文件

```bash
#!/bin/bash
TASK_ID="69a252ad3e86c360f083e06c"
FILES_DIR="/path/to/files"

for file in "$FILES_DIR"/*; do
  uv run scripts/simple-upload.py \
    --file-path "$file" \
    --scope "task:$TASK_ID" \
    --category "attachment"
done
```

## 常见问题

### 如何获取 scope？

```bash
# 查询任务 ID
uv run scripts/query-tasks.py --tql "content ~ '任务名称'"

# 查询项目 ID
uv run scripts/query-projects.py --tql "nameText ~ '项目名称'"
```

### category 选择哪个？

- `attachment` - 任务/项目附件（**最常用，推荐**）
- `rich-text` - 富文本图片
- `work` - 工作文档

### 支持的文件类型

支持所有常见文件：图片（JPG、PNG、GIF）、文档（PDF、DOC、XLS）、压缩包（ZIP）、代码文件等。

### 文件大小限制

- 图片：建议 < 10MB
- 文档：建议 < 50MB
- 最大限制：100MB
- 📝 [最佳实践](BEST_PRACTICES.md) - 使用约束与最佳实践
- 📝 [错误处理](ERROR_HANDLING.md) - 常见错误及解决方案
