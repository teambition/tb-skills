#!/usr/bin/env python3
"""
上传文件到任务的文件类型自定义字段（一站式脚本，支持多文件）
用法: uv run scripts/upload_file_to_customfield.py --task-id <ID> --file-paths <路径> --customfield-id <字段ID>

自动完成流程：
1. 上传每个文件获取 fileToken（scope: task:<taskId>/attachment, category: attachment）
2. 更新任务自定义字段（value 数组包含所有文件的 metaString + title）
"""

import json
import os
import sys
from typing import List, Optional

import call_api


def upload_files_to_customfield(task_id: str, file_paths: List[str], customfield_id: str) -> dict:
    """
    上传一个或多个文件到任务的文件类型自定义字段。

    Args:
        task_id: 任务 ID
        file_paths: 本地文件路径列表
        customfield_id: 自定义字段 ID

    Returns:
        包含上传结果的字典
    """
    scope = f"task:{task_id}/attachment"
    value_items = []
    uploaded = []

    print(f"📤 正在上传 {len(file_paths)} 个文件...", file=sys.stderr)
    for fp in file_paths:
        file_name = os.path.basename(fp)
        file_token = call_api.upload_single_file(fp, scope, "attachment")
        value_items.append({
            "metaString": json.dumps({"fileToken": file_token}, ensure_ascii=False),
            "title": file_name,
        })
        uploaded.append({"fileName": file_name, "fileToken": file_token})

    # 更新任务自定义字段
    print("📝 正在更新自定义字段...", file=sys.stderr)
    payload = {
        "customfieldId": customfield_id,
        "value": value_items,
    }
    result = call_api.post(f"v3/task/{task_id}/customfield/update", payload)

    print(f"✅ {len(file_paths)} 个文件已成功上传到自定义字段！", file=sys.stderr)

    return {
        "success": True,
        "taskId": task_id,
        "customfieldId": customfield_id,
        "files": uploaded,
        "result": result,
    }


def main() -> None:
    if "--help" in sys.argv or len(sys.argv) < 2:
        print("""用法: uv run scripts/upload_file_to_customfield.py --task-id <ID> --file-paths <路径> --customfield-id <字段ID>

必需参数:
  --task-id <ID>           任务 ID
  --file-paths <路径>      本地文件路径，逗号分隔，支持多文件
                           如: '/path/a.pdf' 或 '/path/a.pdf,/path/b.png'
  --customfield-id <ID>    自定义字段 ID

可选:
  --help                   显示帮助

示例:
  # 上传单个文件
  uv run scripts/upload_file_to_customfield.py \\
    --task-id '69b79d53f1c083201b98f83a' \\
    --file-paths '/path/to/document.pdf' \\
    --customfield-id '699eb728848fa96f9be04ef6'

  # 上传多个文件
  uv run scripts/upload_file_to_customfield.py \\
    --task-id '69b79d53f1c083201b98f83a' \\
    --file-paths '/path/a.pdf,/path/b.png' \\
    --customfield-id '699eb728848fa96f9be04ef6'

说明:
  此脚本自动完成以下步骤：
  1. 上传文件到 OSS（scope: task:<taskId>/attachment, category: attachment）
  2. 更新任务的文件类型自定义字段（value 数组包含所有文件）

  查找自定义字段 ID：
  1. 获取任务的 sfcId: uv run scripts/query_task_detail.py <taskId> --detail-level detailed
  2. 获取字段列表: uv run scripts/get_custom_fields.py <projectId> --sfc-id <sfcId>
  3. 找到 type 为 'work' 的字段，其 ID 即为自定义字段 ID""")
        sys.exit(0)

    task_id: Optional[str] = None
    file_paths: Optional[List[str]] = None
    customfield_id: Optional[str] = None

    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--task-id" and i + 1 < len(sys.argv):
            task_id = sys.argv[i + 1]
            i += 2
        elif arg == "--file-paths" and i + 1 < len(sys.argv):
            file_paths = [p.strip() for p in sys.argv[i + 1].split(",") if p.strip()]
            i += 2
        elif arg == "--customfield-id" and i + 1 < len(sys.argv):
            customfield_id = sys.argv[i + 1]
            i += 2
        else:
            print(f"❌ 未知参数: {arg}", file=sys.stderr)
            sys.exit(1)

    if not task_id:
        print("❌ 缺少 --task-id", file=sys.stderr)
        sys.exit(1)
    if not file_paths:
        print("❌ 缺少 --file-paths", file=sys.stderr)
        sys.exit(1)
    if not customfield_id:
        print("❌ 缺少 --customfield-id", file=sys.stderr)
        sys.exit(1)

    result = upload_files_to_customfield(task_id, file_paths, customfield_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()