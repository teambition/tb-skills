# 任务操作参考

本文档覆盖任务的进展、评论、动态、归档/恢复等操作，均通过 `call_api` 直接调用。

## 任务进展

进展用于记录任务执行情况，支持状态标记（正常/风险/逾期）。

### 进展状态

| 值 | 含义 |
|----|------|
| 1 | 正常（默认） |
| 2 | 存在风险 |
| 3 | 逾期 |

### 获取进展列表

```
GET v3/task/{taskId}/traces
```

在脚本中调用：
```python
import call_api
data = call_api.get(f"v3/task/{task_id}/traces")
```

### 创建进展（推荐使用 create_trace.py）

```bash
uv run scripts/create_trace.py \
  --task-id 'xxx' \
  --title '已完成需求评审，进入开发阶段' \
  --status 1
```

状态值：`1`=正常（默认）、`2`=风险、`3`=逾期

### 直接调用 API

```
POST v3/task/{taskId}/trace/create
```

请求体：
```json
{
  "title": "完成需求评审",
  "content": "详细说明（可选）",
  "status": 1,
  "reminderIds": ["userId1", "userId2"]
}
```

在脚本中调用：
```python
import call_api
data = call_api.post(f"v3/task/{task_id}/trace/create", {
    "title": "完成需求评审",
    "content": "已完成，进入开发阶段",
    "status": 1,
})
```

---

## 任务评论

### 创建评论（推荐使用 create_comment.py）

```bash
uv run scripts/create_comment.py \
  --task-id 'xxx' \
  --content '已完成初稿，请 @张三 评审' \
  --mention '张三'
```

### 带附件的评论（使用 --file-paths 自动上传）

```bash
# 单个文件
uv run scripts/create_comment.py \
  --task-id 'xxx' \
  --content '附件请查收' \
  --file-paths '/path/to/doc.pdf'

# 多个文件
uv run scripts/create_comment.py \
  --task-id 'xxx' \
  --content '附件请查收' \
  --file-paths '/path/a.pdf,/path/b.png'
```

### 直接调用 API

```
POST v3/task/{taskId}/comment
```

请求体：
```json
{
  "content": "评论内容",
  "renderMode": "plain",
  "mentionUserIds": ["userId1"],
  "fileTokens": ["fileToken1"]
}
```

---

## 文件上传到自定义字段

将文件上传到任务的文件类型自定义字段（一站式操作，支持多文件）。

### 使用 upload_file_to_customfield.py

```bash
# 上传单个文件
uv run scripts/upload_file_to_customfield.py \
  --task-id 'xxx' \
  --file-paths '/path/to/document.pdf' \
  --customfield-id 'cf_xxx'

# 上传多个文件
uv run scripts/upload_file_to_customfield.py \
  --task-id 'xxx' \
  --file-paths '/path/a.pdf,/path/b.png' \
  --customfield-id 'cf_xxx'
```

### 查找自定义字段 ID

```bash
# 第一步：获取任务的 sfcId
uv run scripts/query_task_detail.py <taskId> --detail-level detailed

# 第二步：获取字段列表
uv run scripts/get_custom_fields.py <projectId> --sfc-id <sfcId>

# 第三步：找到 type 为 'work' 的字段，其 ID 即为文件类型自定义字段 ID
```

---

## 任务动态

查询任务的所有操作历史（评论、状态变更、字段修改等）。

```
GET v3/task/{taskId}/activity/list
```

查询参数：
- `actions`：筛选类型（如 `comment`）
- `excludeActions`：排除类型
- `language`：语言（`zh_CN`）
- `orderBy`：排序（`created_desc`）

在脚本中调用：
```python
import call_api
data = call_api.get(f"v3/task/{task_id}/activity/list", params={"language": "zh_CN"})
```

---

## 归档与恢复

### 归档任务

```
PUT v3/task/{taskId}/archive
```

```python
import call_api
call_api.put(f"v3/task/{task_id}/archive")
```

### 恢复任务

```
POST v3/task/{taskId}/restore
```

```python
import call_api
call_api.post(f"v3/task/{task_id}/restore", {
    "tfsId": "状态ID（可选）",
    "stageId": "任务列ID（可选）",
})
```

---

## 标记完成/未完成

### 推荐方式：通过工作流状态更新（适用于有工作流的任务）

先查询该任务的工作流状态列表，找到 `kind=end` 的完成状态 ID，再更新：

```bash
# 第一步：查询状态列表，找到完成状态的 ID
uv run scripts/get_task_statuses.py <taskId>

# 第二步：更新到完成状态
uv run scripts/update_task.py --task-id <taskId> --taskflowstatus-id <完成状态ID>
```

### 快速标记方式：直接调 isDone API

适用于不关心工作流状态、只需快速标记完成/未完成的场景：

```
PUT v3/task/{taskId}/isDone
```

```python
import call_api
call_api.put(f"v3/task/{task_id}/isDone", {"isDone": True})   # 标记完成
call_api.put(f"v3/task/{task_id}/isDone", {"isDone": False})  # 标记未完成
```
