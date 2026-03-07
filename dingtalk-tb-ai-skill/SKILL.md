---
name: dingtalk-tb-ai-skill
description: "Teambition project management via Python scripts: projects, tasks, task traces, comments, files, members. Use when: (1) querying/creating/updating tasks or projects, (2) managing task progress and comments, (3) uploading files to tasks, (4) querying team members. NOT for: non-Teambition platforms, direct API calls without scripts, or operations not covered by available scripts."
version: 0.0.1
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["python3", "uv"] },
        "primaryEnv": "TB_USER_TOKEN",
        "install":
          [
            {
              "id": "python-brew",
              "kind": "brew",
              "formula": "python",
              "bins": ["python3"],
              "label": "Install Python (brew)",
            },
            {
              "id": "uv-brew",
              "kind": "brew",
              "formula": "uv",
              "bins": ["uv"],
              "label": "Install uv (brew)",
            },
          ],
      },
  }
---

# Teambition Skill

通过 Python 脚本（`uv run`）管理 Teambition 项目、任务和团队协作。

## 适用场景

✅ **适合使用本技能：**

- 通过 TQL 查询项目、任务或任务详情
- 创建、更新或归档任务
- 管理任务进展、评论和动态
- 上传文件到任务
- 查询企业成员或当前用户信息
- 更新任务优先级和状态

## 不适用场景

❌ **不要使用本技能：**

- 操作非 Teambition 平台（Jira、Asana 等）
- 不通过脚本直接调用 REST API
- 管理脚本未覆盖的 Teambition 组织/管理员设置
- Git 操作或代码管理 → 直接使用 `git`

## 环境准备

```bash
# 安装 uv（如未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装依赖
cd dingtalk-tb-ai-skill && uv sync
```

### Token 配置

从 [Teambition 开放平台](https://open.teambition.com/user-mcp) 获取 Token，然后通过以下任一方式配置：

```bash
# 方式 1：环境变量
export TB_USER_TOKEN="your_token_here"

# 方式 2：Claw 配置文件（~/.openclaw/openclaw.json）
 { "skills": { "entries": { "dingtalk-tb-ai-skill": { "enabled": true, "env": { "TB_USER_TOKEN": "your_token" } } } } }

```

## 任务查询完整指南

使用 TQL（任务查询语言）查询 Teambition 任务，支持分页，默认自动获取简单详情。

### 查询任务列表

```bash
uv run scripts/query-tasks.py [选项]
```

**参数说明：**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `--tql` | 字符串 | 否 | 任务查询语言，用于筛选任务 |
| `--page-size` | 整数 | 否 | 每页大小，默认由 API 决定 |
| `--page-token` | 字符串 | 否 | 分页令牌，用于获取下一页 |
| `--no-details` | 布尔 | 否 | 不自动获取任务详情（默认会自动获取简单详情） |

### TQL 快速参考

| 场景 | TQL 表达式 |
|------|-----------|
| 我的待办任务 | `executorId = me() AND isDone = false` |
| 我的已完成任务 | `executorId = me() AND isDone = true` |
| 我的逾期任务 | `executorId = me() AND isDone = false AND dueDate < startOf(d)` |
| 本周任务 | `dueDate <= endOf(w) AND dueDate >= startOf(w)` |
| 今天到期的任务 | `dueDate <= endOf(d) AND dueDate >= startOf(d)` |
| 高优先级任务 | `priority = 0` |
| 某项目的任务 | `projectId = '项目ID'` |
| 查询标题包含关键词的任务 | `title ~ '关键词'` |
| 本周创建的任务 | `created <= endOf(w) AND created >= startOf(w)` |
| 过去7天更新的任务 | `updated >= startOf(d, -7d)` |

**完整 TQL 参考**：请查看 [任务 TQL 参考文档](references/general/TQL_REFERENCE.md)

### 常用查询示例

```bash
# 查询我的待办任务
uv run scripts/query-tasks.py --tql "executorId = me() AND isDone = false"

# 查询特定项目的任务
uv run scripts/query-tasks.py --tql "projectId = '项目ID'"

# 本周创建的任务，按创建时间降序
uv run scripts/query-tasks.py --tql "created <= endOf(w) AND created >= startOf(w) ORDER BY created DESC"

# 过去 7 天更新过的我的任务，按更新时间降序
uv run scripts/query-tasks.py --tql "executorId = me() AND updated >= startOf(d, -7d) ORDER BY updated DESC"

# 我的逾期未完成任务，按截止时间升序
uv run scripts/query-tasks.py --tql "executorId = me() AND isDone = false AND dueDate < startOf(d) ORDER BY dueDate ASC"

# 查询标题包含关键词的任务
uv run scripts/query-tasks.py --tql "title ~ '需求'"

# 只查询任务ID，不获取详情
uv run scripts/query-tasks.py --no-details

# 组合使用多个参数
uv run scripts/query-tasks.py --tql "executorId = me() AND isDone = false" --page-size 20
```

### 查询任务详情

根据任务 ID 查询任务的详细信息，支持简单和详细两种信息级别。

```bash
uv run scripts/query-tasks-detail.py <任务ID> [选项]
```

**参数说明：**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `任务ID` | 字符串 | 是 | 任务 ID 集合，使用逗号分隔 |
| `--detail-level` | 字符串 | 否 | 详细程度：`simple`（默认）或 `detailed` |
| `--extra-fields` | 字符串 | 否 | 简单模式下额外包含的字段，逗号分隔 |

**简单信息（simple，默认）包含字段：**

| 字段 | 说明 |
|------|------|
| `id` | 任务 ID |
| `content` | 任务标题 |
| `isDone` | 是否完成 |
| `executorId` | 执行人 ID |
| `projectId` | 项目 ID |
| `dueDate` | 截止时间 |
| `priority` | 优先级（0=紧急，1=高，2=中，3=低） |
| `created` | 创建时间 |
| `updated` | 更新时间 |

**详细信息（detailed）** 额外包含：`note`（备注）、`sprintId`（迭代 ID）、`stageId`（任务列 ID）、`startDate`（开始时间）、`progress`（进度）、`parentTaskId`（父任务 ID）、自定义字段等 30+ 个字段。

```bash
# 查询单个任务（简单信息）
uv run scripts/query-tasks-detail.py 67ec9b8c3c6130ac88605c3e

# 查询详细信息
uv run scripts/query-tasks-detail.py 67ec9b8c3c6130ac88605c3e --detail-level detailed
```

**更多任务管理功能**（归档、恢复、评论、动态、进展等）请查看 [任务管理完整文档](references/task.md)

---

## 项目查询完整指南

使用 TQL（项目查询语言）查询 Teambition 项目，支持分页，默认自动获取简单详情。

### 查询项目列表

```bash
uv run scripts/query-projects.py [选项]
```

**参数说明：**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `--tql` | 字符串 | 否 | 项目查询语言，用于筛选项目 |
| `--page-size` | 整数 | 否 | 每页大小，默认由 API 决定 |
| `--page-token` | 字符串 | 否 | 分页令牌，用于获取下一页 |
| `--include-template` | 布尔 | 否 | 是否包含模板项目，默认不包含 |
| `--no-details` | 布尔 | 否 | 不自动获取项目详情 |

### TQL 快速参考

| 场景 | TQL 表达式 |
|------|-----------|
| 我创建的项目 | `creatorId = me()` |
| 我参与的项目 | `involveMembers = me()` |
| 按名称搜索 | `nameText ~ '测试'` |
| 已归档的项目 | `isSuspended = true` |
| 今天更新的项目 | `updated <= endOf(d) AND updated >= startOf(d)` |
| 最近7天创建 | `created <= endOf(d, -1d) AND created >= startOf(d, -7d)` |
| 今天创建的项目 | `created <= endOf(d) AND created >= startOf(d)` |
| 本周创建的项目 | `created <= endOf(w) AND created >= startOf(w)` |
| 本月创建的项目 | `created <= endOf(M) AND created >= startOf(M)` |
| 指定日期之后创建 | `created >= '2026-03-01T00:00:00.000Z'` |
| 指定日期之前创建 | `created <= '2026-03-31T23:59:59.999Z'` |
| 指定日期范围创建 | `created >= '2026-03-01T00:00:00.000Z' AND created <= '2026-03-31T23:59:59.999Z'` |

**完整 TQL 参考**：请查看 [项目 TQL 参考文档](references/general/PROJECT_TQL_REFERENCE.md)

**注意**：项目没有截止时间（dueDate）字段，只有创建时间（created）和更新时间（updated）。

### 常用查询示例

```bash
# 查询我创建的项目
uv run scripts/query-projects.py --tql "creatorId = me()"

# 查询我参与的项目
uv run scripts/query-projects.py --tql "involveMembers = me()"

# 按名称搜索项目
uv run scripts/query-projects.py --tql "nameText ~ '产品开发'"

# 本周创建的项目，按创建时间降序
uv run scripts/query-projects.py --tql "created <= endOf(w) AND created >= startOf(w) ORDER BY created DESC"

# 今天更新过的项目，按更新时间降序
uv run scripts/query-projects.py --tql "updated <= endOf(d) AND updated >= startOf(d) ORDER BY updated DESC"

# 过去 7 天创建的我参与的非模板项目
uv run scripts/query-projects.py --tql "isTemplate = false AND involveMembers = me() AND created >= startOf(d, -7d) ORDER BY created DESC"

# 查询已归档的项目
uv run scripts/query-projects.py --tql "isSuspended = true"

# 查询本月创建且我参与的项目
uv run scripts/query-projects.py --tql "created >= startOf(M) AND involveMembers = me()"
```

### 查询项目详情

根据项目 ID 查询项目的详细信息，支持简单和详细两种信息级别。

```bash
uv run scripts/query-projects-detail.py <项目ID> [选项]
```

**参数说明：**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `项目ID` | 字符串 | 是 | 项目 ID 集合，使用逗号分隔 |
| `--detail-level` | 字符串 | 否 | 详细程度：`simple`（默认）或 `detailed` |
| `--extra-fields` | 字符串 | 否 | 简单模式下额外包含的字段，逗号分隔 |

**简单信息（simple，默认）包含字段：**

| 字段 | 说明 |
|------|------|
| `id` | 项目 ID |
| `name` | 项目名称 |
| `description` | 项目描述 |
| `visibility` | 可见性（public/private） |
| `isTemplate` | 是否是模板项目 |
| `creatorId` | 创建人 ID |
| `isArchived` | 是否在回收站 |
| `isSuspended` | 是否已归档 |
| `created` | 创建时间 |
| `updated` | 更新时间 |

**详细信息（detailed）** 额外包含：`logo`（项目 LOGO）、`organizationId`（企业 ID）、`uniqueIdPrefix`（任务 ID 前缀）、`startDate`（开始时间）、`endDate`（结束时间）等 20+ 个字段。

```bash
# 查询单个项目（简单信息）
uv run scripts/query-projects-detail.py 67ec9b8c3c6130ac88605c3e

# 查询详细信息
uv run scripts/query-projects-detail.py 67ec9b8c3c6130ac88605c3e --detail-level detailed

# 查询多个项目
uv run scripts/query-projects-detail.py 67ec9b8c3c6130ac88605c3e,67ec9b8c3c6130ac88605c3f
```

**更多项目管理功能**请查看 [项目管理完整文档](references/project.md)

---

## 常用命令

### 用户与成员

```bash
# 获取当前用户信息
uv run scripts/get-current-user.py

# 按关键字或 ID 搜索成员
uv run scripts/query-members.py --keyword "张三"
```

### 任务 — 创建

```bash
# 基本创建
uv run scripts/create-task.py \
  --project-id "项目ID" \
  --content "任务标题"

# 完整参数创建
uv run scripts/create-task.py \
  --project-id "项目ID" \
  --content "任务标题" \
  --executor-id "执行者ID" \
  --start-date "2026-03-15" \
  --due-date "2026-03-20" \
  --priority "1" \
  --note "任务描述"
```

### 任务 — 更新

```bash
# 更新任务状态
uv run scripts/update-task-status.py --task-id "任务ID" --status-id "状态ID"

# 更新优先级（0=紧急, 1=高, 2=中, 3=低）
uv run scripts/user-update-task-priority.py --task-id "任务ID" --priority "0"

# 更新任务备注
uv run scripts/update-task-note.py --task-id "任务ID" --note "更新后的备注"
```

### 任务 — 归档与恢复

```bash
# 归档任务（移入回收站）
uv run scripts/call-user-api.py PUT "v3/task/任务ID/archive"

# 恢复任务
uv run scripts/call-user-api.py POST "v3/task/任务ID/restore" '{}'
```

### 任务评论与动态

```bash
# 创建评论（支持附件和 @提及）
uv run scripts/call-user-api.py POST "v3/task/任务ID/comment" '{"content": "评论内容"}'

# 查询任务动态
uv run scripts/call-user-api.py GET "v3/task/任务ID/activity/list"
```

### 任务进展

```bash
# 获取任务进展列表
uv run scripts/call-user-api.py GET "v3/task/任务ID/traces"

# 创建任务进展
uv run scripts/call-user-api.py POST "v3/task/任务ID/trace/create" '{"title":"已完成需求分析","content":""}'
```

### 文件上传

```bash
# 上传文件到任务
uv run scripts/upload-file.py --task-id "任务ID" --file-path "/path/to/file"
```

## 分页查询

大多数查询命令支持分页：

- `--page-size`：每页记录数（默认 30，最大 100）
- `--page-token`：传入上次返回的 `nextPageToken` 获取下一页

```bash
# 第一页
uv run scripts/query-tasks.py --tql "executorId = me()" --page-size 20

# 下一页（使用上次返回的 nextPageToken）
uv run scripts/query-tasks.py --tql "executorId = me()" --page-size 20 --page-token "上次返回的TOKEN"
```

## 日期时区转换

日期需从东八区（用户输入）转换为 UTC（API 格式）：

- **用户输入**：`2026-03-15`（东八区）
- **API 格式**：`2026-03-14T16:00:00.000Z`（UTC，减去 8 小时）

```python
from datetime import datetime, timedelta

user_date = "2026-03-15"
dt = datetime.strptime(user_date, "%Y-%m-%d") - timedelta(hours=8)
iso_date = dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
# 结果：2026-03-14T16:00:00.000Z
```

## 参考文档

- [创建任务](references/create-task.md) — 任务创建完整指南（字段映射、自定义字段、辅助脚本）
- [更新任务](references/update-task.md) — 更新任务各字段详细指南（并行更新、自定义字段）
- [用户与成员](references/user.md) — 获取当前用户信息、查询企业成员
- [优先级](references/priority.md) — 查询企业优先级配置、更新任务优先级
- [任务管理](references/task.md) — 任务查询和管理完整参考（归档、恢复、评论、动态、进展）
- [项目管理](references/project.md) — 项目查询完整参考（TQL 筛选、详情级别）
- [任务进展](references/task-trace.md) — 进展跟踪（获取/创建进展、状态标记）
- [文件上传](references/file-upload.md) — 上传文件到任务或项目
- [TQL 参考](references/general/TQL_REFERENCE.md) — 任务查询语言完整语法
- [项目 TQL](references/general/PROJECT_TQL_REFERENCE.md) — 项目查询语言完整语法
- [最佳实践](references/general/BEST_PRACTICES.md) — 使用约束与最佳实践
- [错误处理](references/general/ERROR_HANDLING.md) — 常见错误及解决方案

## 注意事项

- 运行脚本前先 `cd dingtalk-tb-ai-skill`
- 在 TQL 中使用 `me()` 表示当前认证用户
- 使用不熟悉的字段前先查阅参考文档，不要猜测参数名
- 优先级值：`0`=紧急、`1`=高、`2`=中、`3`=低
- 创建任务时日期转为 UTC，查询展示时转回东八区
- 首次操作建议在测试项目中验证