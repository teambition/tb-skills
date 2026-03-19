#!/usr/bin/env python3
"""
查询 Teambition 任务动态（操作历史）
用法: uv run scripts/query_task_activity.py --task-id <ID> [选项]

动态类型: comment=评论 status_change=状态变更 executor_change=执行人变更
         priority_change=优先级变更 due_date_change=截止时间变更
"""

import json
import sys
from typing import Any, Dict, List, Optional

import call_api

def get_file_download_urls(
    task_id: str,
    activity_id: str,
    file_ids: List[str],
) -> Dict[str, str]:
    """
    获取评论附件的下载链接。
    返回 {file_id: downloadUrl} 映射。
    """
    if not file_ids:
        return {}

    resource_ids = [
        f"task:{task_id}/activity:{activity_id}/file:{file_id}"
        for file_id in file_ids
    ]

    try:
        resp = call_api.post(
            "v3/file/query/by-resource-ids",
            body={
                "needSign": True,
                "resourceIds": resource_ids,
                "expireAfterSeconds": 604800,  # 7天有效期
            },
            headers={"X-Canary": "prepub"}
        )
        files = resp.get("result", [])
        return {f.get("resourceId", "").split("/")[-1]: f.get("downloadUrl", "") for f in files if f.get("downloadUrl")}
    except Exception as e:
        print(f"⚠️ 获取文件下载链接失败: {e}", file=sys.stderr)
        return {}

def enrich_comment_with_file_urls(
    task_id: str,
    activity: Dict[str, Any],
) -> Dict[str, Any]:
    """
    为评论动态补充文件附件的下载链接。
    """
    if activity.get("action") != "comment":
        return activity

    content = activity.get("content", "")
    try:
        content_data = json.loads(content)
    except json.JSONDecodeError:
        return activity

    file_ids = content_data.get("files", [])
    if not file_ids:
        return activity

    activity_id = activity.get("id", "")
    file_urls = get_file_download_urls(task_id, activity_id, file_ids)

    # 将下载链接添加到 content_data 中
    content_data["fileUrls"] = file_urls
    activity["content"] = json.dumps(content_data, ensure_ascii=False)
    activity["attachments"] = [
        {"fileId": fid, "downloadUrl": file_urls.get(fid, "")}
        for fid in file_ids
    ]

    return activity

def query_activity(
    task_id: str,
    actions: Optional[str] = None,
    exclude_actions: Optional[str] = None,
    language: str = "zh_CN",
    order_by: str = "created_desc",
    page_size: Optional[int] = None,
    enrich_files: bool = False,
) -> None:
    params: dict = {"language": language, "orderBy": order_by}
    if actions:
        params["actions"] = actions
    if exclude_actions:
        params["excludeActions"] = exclude_actions
    if page_size:
        params["pageSize"] = page_size

    data = call_api.get(f"v3/task/{task_id}/activity/list", params=params)
    result = data.get("result", data)

    # 如果启用文件链接补充，处理评论类型的动态
    if enrich_files and isinstance(result, list):
        for i, activity in enumerate(result):
            if activity.get("action") == "comment":
                result[i] = enrich_comment_with_file_urls(task_id, activity)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    count = len(result) if isinstance(result, list) else "?"
    print(f"共找到 {count} 条动态记录", file=sys.stderr)

def main() -> None:
    if "--help" in sys.argv:
        print("""用法: uv run scripts/query_task_activity.py --task-id <ID> [选项]

必需:
  --task-id <ID>          任务 ID

可选:
  --actions <类型>        只查询指定类型（如 comment）
  --exclude-actions <类型> 排除指定类型
  --language <语言>       语言（默认 zh_CN）
  --order-by <排序>       排序方式（默认 created_desc）
  --page-size <数量>      每页数量
  --no-enrich-files       禁用评论附件下载链接补充（默认启用）
  --help                  显示帮助

示例:
  uv run scripts/query_task_activity.py --task-id '69b2ad9501c321cc9c927eaf'
  uv run scripts/query_task_activity.py --task-id '69b2ad9501c321cc9c927eaf' --actions comment
  uv run scripts/query_task_activity.py --task-id '69b2ad9501c321cc9c927eaf' --actions comment --enrich-files
  uv run scripts/query_task_activity.py --task-id '69b2ad9501c321cc9c927eaf' --exclude-actions comment""")
        sys.exit(0)

    task_id: Optional[str] = None
    actions: Optional[str] = None
    exclude_actions: Optional[str] = None
    language = "zh_CN"
    order_by = "created_desc"
    page_size: Optional[int] = None
    enrich_files = True  # 默认开启文件链接补充

    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--task-id" and i + 1 < len(sys.argv):
            task_id = sys.argv[i + 1]; i += 2
        elif arg == "--actions" and i + 1 < len(sys.argv):
            actions = sys.argv[i + 1]; i += 2
        elif arg == "--exclude-actions" and i + 1 < len(sys.argv):
            exclude_actions = sys.argv[i + 1]; i += 2
        elif arg == "--language" and i + 1 < len(sys.argv):
            language = sys.argv[i + 1]; i += 2
        elif arg == "--order-by" and i + 1 < len(sys.argv):
            order_by = sys.argv[i + 1]; i += 2
        elif arg == "--page-size" and i + 1 < len(sys.argv):
            page_size = int(sys.argv[i + 1]); i += 2
        elif arg == "--no-enrich-files":
            enrich_files = False; i += 1
        else:
            print(f"❌ 未知参数: {arg}", file=sys.stderr)
            sys.exit(1)

    if not task_id:
        print("❌ 缺少 --task-id", file=sys.stderr)
        sys.exit(1)

    query_activity(task_id, actions, exclude_actions, language, order_by, page_size, enrich_files)

if __name__ == "__main__":
    main()