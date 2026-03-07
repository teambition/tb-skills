# 任务管理

本文档介绍如何使用 Teambition API 查询任务列表和任务详情。

## ⚠️ 重要约束

在进行任务相关操作时，请遵守以下约束：

1. **优先使用文档提供的方式和脚本**：查询任务、更新任务、创建任务等操作时，优先使用本文档中已提供的方式和脚本，而不是直接调用底层 API。文档中的脚本已经过充分测试和优化，能够提供更好的用户体验和错误处理。

## 功能列表

- [创建任务](#创建任务)
- [更新任务](#更新任务)
- [归档任务](#归档任务)
- [恢复任务](#恢复任务)
- [查询任务列表](#查询任务列表)
- [查询任务详情](#查询任务详情)
- [任务进展管理](#任务进展管理)
- [任务评论](#任务评论)
- [任务动态](#任务动态)

---

## 创建任务

创建 Teambition 任务，支持智能项目选择、任务类型配置和自定义字段处理。

### 快速开始

```bash
# 最简单的创建方式
uv run scripts/create-task.py --content '完成需求文档'
```

### 详细文档

创建任务功能较为复杂，包含项目选择、任务类型配置、自定义字段处理等多个步骤。

**完整文档**：请查看 [创建任务详细文档](create-task.md)

---

## 更新任务

更新 Teambition 任务的各个字段，支持并行执行多个字段更新。

### 快速开始

```bash
# 更新单个字段
uv run scripts/update-task.py \
  --task-id '67f0a1b2c3d4e5f6g7h8i9j0' \
  --content '新的任务标题'

# 更新多个字段（并行执行）
uv run scripts/update-task.py \
  --task-id '67f0a1b2c3d4e5f6g7h8i9j0' \
  --content '更新后的标题' \
  --executor-id '696f2c084a459842b42b035b' \
  --due-date '2026-03-15T00:00:00.000Z' \
  --priority 1
```

### 详细文档

任务更新功能支持更新任务的各种属性，包括标题、执行人、日期、优先级、参与者等。

**完整文档**：请查看 [更新任务详细文档](update-task.md)

### 核心特性

- **并行执行**：多个字段同时更新，显著提升性能
- **增量更新**：只修改指定字段，不影响其他字段
- **灵活参与者管理**：支持完全替换、增量添加、增量删除

### 支持的更新字段

| 字段 | 说明 |
|------|------|
| `content` | 任务标题 |
| `executorId` | 执行人 ID |
| `dueDate` | 截止日期 |
| `startDate` | 开始日期 |
| `note` | 任务备注 |
| `priority` | 优先级（0-3） |
| `storyPoint` | 故事点 |
| `taskflowstatusId` | 任务状态 ID |
| `involveMembers` | 参与者列表 |
| `customfields` | 自定义字段 |

### 常用示例

```bash
# 更新任务标题
uv run scripts/update-task.py \
  --task-id '67f0a1b2c3d4e5f6g7h8i9j0' \
  --content '新的任务标题'

# 更新执行人和截止日期
uv run scripts/update-task.py \
  --task-id '67f0a1b2c3d4e5f6g7h8i9j0' \
  --executor-id '696f2c084a459842b42b035b' \
  --due-date '2026-03-20T23:59:59.999Z'

# 增量添加参与者
uv run scripts/update-task.py \
  --task-id '67f0a1b2c3d4e5f6g7h8i9j0' \
  --add-involvers '["696f2c084a459842b42b035d"]'

# 更新多个字段（并行执行，性能优势明显）
uv run scripts/update-task.py \
  --task-id '67f0a1b2c3d4e5f6g7h8i9j0' \
  --content '更新后的标题' \
  --executor-id '696f2c084a459842b42b035b' \
  --due-date '2026-03-15T23:59:59.999Z' \
  --priority 1 \
  --note '更新后的备注'
```

---

## 归档任务

将任务移入回收站（归档）。归档后的任务不会显示在正常的任务列表中，但可以通过恢复操作重新激活。

### 快速开始

```bash
# 归档指定任务
uv run scripts/call-user-api.py PUT "v3/task/67ec9b8c3c6130ac88605c3e/archive"
```

### API 接口说明

**接口信息：**
- **方法**：PUT
- **路径**：`v3/task/{taskId}/archive`
- **参数**：
  - `taskId`（路径参数，必填）：任务 ID

### 使用示例

```bash
# 归档任务
uv run scripts/call-user-api.py PUT "v3/task/67ec9b8c3c6130ac88605c3e/archive"

# 归档多个任务（需要分别调用）
uv run scripts/call-user-api.py PUT "v3/task/67ec9b8c3c6130ac88605c3e/archive"
uv run scripts/call-user-api.py PUT "v3/task/67ec9b8c3c6130ac88605c3f/archive"
```

### 响应说明

成功归档后，API 会返回任务的更新时间：

```json
{
  "updated": "2026-02-28T07:30:00.000Z"
}
```

### 注意事项

- 归档的任务会移入回收站，不会在正常任务列表中显示
- 归档的任务可以通过恢复接口重新激活
- 归档操作不会删除任务数据，只是改变任务的显示状态

---

## 恢复任务

将已归档的任务从回收站恢复到正常状态。恢复时可以指定任务的状态、类型、任务列和迭代等信息。

### 快速开始

```bash
# 恢复任务（使用默认配置）
uv run scripts/call-user-api.py POST "v3/task/67ec9b8c3c6130ac88605c3e/restore" '{}'

# 恢复任务并指定状态和任务列
uv run scripts/call-user-api.py POST "v3/task/67ec9b8c3c6130ac88605c3e/restore" \
  '{"tfsId":"67ec9b8c3c6130ac88605c45","stageId":"67ec9b8c3c6130ac88605c46"}'
```

### API 接口说明

**接口信息：**
- **方法**：POST
- **路径**：`v3/task/{taskId}/restore`
- **参数**：
  - `taskId`（路径参数，必填）：任务 ID
  - 请求体（JSON，可选）：
    - `tfsId`（可选）：任务状态 ID
    - `sfcId`（可选）：任务类型 ID
    - `stageId`（可选）：任务列 ID
    - `sprintId`（可选）：迭代 ID

### 使用示例

```bash
# 恢复任务（使用默认配置）
uv run scripts/call-user-api.py POST "v3/task/67ec9b8c3c6130ac88605c3e/restore" '{}'

# 恢复任务并指定状态
uv run scripts/call-user-api.py POST "v3/task/67ec9b8c3c6130ac88605c3e/restore" \
  '{"tfsId":"67ec9b8c3c6130ac88605c45"}'

# 恢复任务并指定完整配置
uv run scripts/call-user-api.py POST "v3/task/67ec9b8c3c6130ac88605c3e/restore" \
  '{"tfsId":"67ec9b8c3c6130ac88605c45","sfcId":"67ec9b8c3c6130ac88605c44","stageId":"67ec9b8c3c6130ac88605c46","sprintId":"67ec9b8c3c6130ac88605c47"}'
```

### 参数说明

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `taskId` | string | 是 | 任务 ID（路径参数） |
| `tfsId` | string | 否 | 任务状态 ID，不指定则使用默认状态 |
| `sfcId` | string | 否 | 任务类型 ID，不指定则使用默认类型 |
| `stageId` | string | 否 | 任务列 ID，不指定则使用默认任务列 |
| `sprintId` | string | 否 | 迭代 ID，不指定则不关联迭代 |

### 响应说明

成功恢复后，API 会返回任务的更新时间：

```json
{
  "updated": "2026-02-28T07:30:00.000Z"
}
```

### 注意事项

- 恢复任务时，如果不指定状态、类型等参数，系统会使用默认配置
- 建议在恢复前先查询项目的工作流状态和任务列信息，确保指定的 ID 有效
- 恢复后的任务会重新出现在正常的任务列表中

---

## 查询任务列表

使用 TQL（任务查询语言）查询 Teambition 任务，支持分页，默认自动获取简单详情。

### 基本用法

```bash
uv run scripts/query-tasks.py [选项]
```

### 参数说明

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `--tql` | 字符串 | 否 | 任务查询语言，用于筛选任务 |
| `--page-size` | 整数 | 否 | 每页大小，默认由 API 决定 |
| `--page-token` | 字符串 | 否 | 分页令牌，用于获取下一页 |
| `--no-details` | 布尔 | 否 | 不自动获取任务详情（默认会自动获取简单详情） |
| `--help` | 布尔 | 否 | 显示帮助信息 |

### TQL 快速参考

| 场景 | TQL 表达式                                                         |
|------|-----------------------------------------------------------------|
| 我的待办任务 | `executorId = me() AND isDone = false`                          |
| 我的已完成任务 | `executorId = me() AND isDone = true`                           |
| 我的逾期任务 | `executorId = me() AND isDone = false AND dueDate < startOf(d)` |
| 本周任务 | `dueDate <= endOf(w) AND dueDate >= startOf(w)`                 |
| 今天到期的任务 | `dueDate <= endOf(d) AND dueDate >= startOf(d)`                 |
| 高优先级任务 | `priority = 0`                                                  |
| 某项目的任务 | `projectId = '项目ID'`                                            |
| 查询标题包含关键词的任务 | `title ~ '关键词'`                                                 |

**完整 TQL 参考**：请查看 [任务 TQL 参考文档](TQL_REFERENCE.md)

### 使用示例

```bash
# 显示帮助信息
uv run scripts/query-tasks.py --help

# 查询所有任务（自动获取详情）
uv run scripts/query-tasks.py

# 查询我的待办任务
uv run scripts/query-tasks.py --tql "executorId = me() AND isDone = false"

# 查询某个项目的任务
uv run scripts/query-tasks.py --tql "projectId = '67ec9b8c3c6130ac88605c3e'"

# 设置每页大小
uv run scripts/query-tasks.py --page-size 50

# 只查询任务ID，不获取详情
uv run scripts/query-tasks.py --no-details

# 使用分页令牌获取下一页
uv run scripts/query-tasks.py --page-token "DXF1ZXJ5QW5kRmV0Y2gBAAAAAgvq5FcWdUtmQWRmLXBSN2VjZmJSLWUyQTV5dw=="

# 组合使用多个参数
uv run scripts/query-tasks.py --tql "executorId = me() AND isDone = false" --page-size 20
```

---

## 查询任务详情

根据任务 ID 查询任务的详细信息，支持简单和详细两种信息级别。

### 基本用法

```bash
uv run scripts/query-tasks-detail.py <任务ID> [选项]
```

### 参数说明

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `任务ID` | 字符串 | 是 | 任务 ID 集合，使用逗号分隔 |
| `--detail-level` | 字符串 | 否 | 详细程度：`simple`（默认）或 `detailed` |
| `--extra-fields` | 字符串 | 否 | 简单模式下额外包含的字段，逗号分隔 |

### 信息级别

#### 简单信息（simple）

默认包含的字段：

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

#### 详细信息（detailed）

包含所有 API 返回的字段（30+ 个字段），包括：
- 所有简单信息字段
- `note`：任务备注
- `sprintId`：迭代 ID
- `stageId`：任务列 ID
- `startDate`：开始时间
- `progress`：任务进度
- `parentTaskId`：父任务 ID
- 自定义字段等

### 使用示例

```bash
# 查询单个任务
uv run scripts/query-tasks-detail.py 67ec9b8c3c6130ac88605c3e

# 查询详细信息
uv run scripts/query-tasks-detail.py 67ec9b8c3c6130ac88605c3e --detail-level detailed
```

### 优先级说明

| 值 | 优先级 |
|----|--------|
| 0 | 紧急 |
| 1 | 高 |
| 2 | 中 |
| 3 | 低 |

---

## 任务进展管理

任务进展用于记录任务的执行情况和最新动态，帮助团队成员了解任务的实时状态。

### 快速开始

```bash
# 获取任务进展列表
uv run scripts/call-user-api.py GET "v3/task/67ec9b8c3c6130ac88605c3e/traces"

# 创建任务进展
uv run scripts/call-user-api.py POST "v3/task/67ec9b8c3c6130ac88605c3e/trace/create" \
  '{"title":"完成需求分析","content":""}'
```

### 详细文档

任务进展功能包括获取进展列表、创建新进展、标记进展状态等。

**完整文档**：请查看 [任务进展管理文档](task-trace.md)

### 核心特性

- **📋 进展列表**：获取任务的所有进展记录
- **✍️ 创建进展**：记录任务的最新动态
- **🚦 状态标记**：标记进展状态（正常/风险/逾期）
- **👥 提醒功能**：提醒相关人员关注进展
- **📎 附件支持**：支持上传附件（通过 API）

### 进展状态

| 状态值 | 状态名称 | 说明 |
|--------|---------|------|
| 1 | 正常 | 任务进展顺利 |
| 2 | 存在风险 | 任务遇到问题或风险 |
| 3 | 逾期 | 任务进度延期 |

### 常用示例

```bash
# 获取任务进展
uv run scripts/call-user-api.py GET "v3/task/67ec9b8c3c6130ac88605c3e/traces"

# 创建进展
uv run scripts/call-user-api.py POST "v3/task/67ec9b8c3c6130ac88605c3e/trace/create" \
  '{"title":"完成开发","content":"已完成核心功能开发"}'
```

---

## 任务评论

为任务添加评论，支持纯文本、Markdown 格式、附件和 @ 成员等功能。

### 快速开始

```bash
# 创建简单评论
uv run scripts/call-user-api.py POST "v3/task/67ec9b8c3c6130ac88605c3e/comment" \
  '{"content":"已完成需求分析"}'
```

### API 接口说明

**接口信息：**
- **方法**：POST
- **路径**：`v3/task/{taskId}/comment`
- **参数**：
  - `taskId`（路径参数，必填）：任务 ID
  - 请求体（JSON）：
    - `content`（必填）：评论内容
    - `renderMode`（可选）：渲染模式，默认原文
    - `fileTokens`（可选）：附件 token 数组，最多 30 个
    - `mentionUserIds`（可选）：@ 成员 ID 数组，最多 30 个

### 创建任务评论

为指定任务创建评论，支持多种格式和功能。

#### 基本用法

```bash
uv run scripts/call-user-api.py POST "v3/task/<任务ID>/comment" '<JSON数据>'
```

### 使用示例

```bash
# 创建简单评论
uv run scripts/call-user-api.py POST "v3/task/67ec9b8c3c6130ac88605c3e/comment" \
  '{"content":"已完成需求分析"}'

# Markdown 格式评论
uv run scripts/call-user-api.py POST "v3/task/67ec9b8c3c6130ac88605c3e/comment" \
  '{"content":"## 进展更新\n\n- [x] 需求分析\n- [ ] 开发实现","renderMode":"markdown"}'

# @ 成员
uv run scripts/call-user-api.py POST "v3/task/67ec9b8c3c6130ac88605c3e/comment" \
  '{"content":"@张三 请评审","mentionUserIds":["696f2c084a459842b42b035b"]}'
```

### 参数说明

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `taskId` | string | 是 | 任务 ID（路径参数） |
| `content` | string | 是 | 评论内容 |
| `renderMode` | string | 否 | 渲染模式：`plain` 或 `markdown`，默认 `plain` |
| `fileTokens` | array | 否 | 附件 token 数组，最多 30 个 |
| `mentionUserIds` | array | 否 | @ 成员 ID 数组，最多 30 个 |

---

## 任务动态

查询任务的所有动态记录，包括评论、状态变更、字段修改等操作历史。支持按类型筛选、分页查询和多语言显示。

### 快速开始

```bash
# 查询所有动态
uv run scripts/call-user-api.py GET "v3/task/67ec9b8c3c6130ac88605c3e/activity/list"

# 只查询评论
uv run scripts/call-user-api.py GET "v3/task/67ec9b8c3c6130ac88605c3e/activity/list?actions=comment"

# 查询非评论动态
uv run scripts/call-user-api.py GET "v3/task/67ec9b8c3c6130ac88605c3e/activity/list?excludeActions=comment"
```

### API 接口说明

**接口信息：**
- **方法**：GET
- **路径**：`v3/task/{taskId}/activity/list`
- **参数**：
  - `taskId`（路径参数，必填）：任务 ID
  - 查询参数（可选）：
    - `pageSize`：分页大小
    - `pageToken`：分页令牌
    - `actions`：筛选动态类型（逗号分隔）
    - `excludeActions`：排除动态类型（逗号分隔）
    - `creatorIds`：按创建人筛选（逗号分隔）
    - `language`：语言（zh_CN, zh_TW, en_US）
    - `orderBy`：排序方式

### 查询任务动态

获取指定任务的动态记录，支持多种筛选和排序方式。

#### 基本用法

```bash
uv run scripts/call-user-api.py GET "v3/task/<任务ID>/activity/list[?参数]"
```

### 使用示例

```bash
# 查询所有动态
uv run scripts/call-user-api.py GET "v3/task/67ec9b8c3c6130ac88605c3e/activity/list"

# 只查询评论
uv run scripts/call-user-api.py GET "v3/task/67ec9b8c3c6130ac88605c3e/activity/list?actions=comment"

# 查询非评论动态
uv run scripts/call-user-api.py GET "v3/task/67ec9b8c3c6130ac88605c3e/activity/list?excludeActions=comment"

# 获取中文描述
uv run scripts/call-user-api.py GET "v3/task/67ec9b8c3c6130ac88605c3e/activity/list?language=zh_CN"
```

### 参数说明

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `taskId` | string | 是 | 任务 ID（路径参数） |
| `pageSize` | integer | 否 | 分页大小 |
| `pageToken` | string | 否 | 分页令牌 |
| `actions` | string | 否 | 筛选动态类型，逗号分隔 |
| `excludeActions` | string | 否 | 排除动态类型，逗号分隔 |
| `creatorIds` | string | 否 | 按创建人筛选，逗号分隔 |
| `language` | string | 否 | 语言（zh_CN, zh_TW, en_US） |
| `orderBy` | string | 否 | 排序方式（created, created_desc, updated, updated_desc） |

### 动态类型说明

常见的动态类型（action）：

| 动态类型 | 说明 |
|---------|------|
| `comment` | 评论 |
| `status_change` | 状态变更 |
| `executor_change` | 执行人变更 |
| `priority_change` | 优先级变更 |
| `due_date_change` | 截止时间变更 |
| `content_change` | 标题变更 |

**能力拆分：**
- **查询评论**：使用 `actions=comment`
- **查询非评论动态**：使用 `excludeActions=comment`

---

## 相关文档

- [创建任务](create-task.md) - 创建任务完整指南
- [更新任务](update-task.md) - 更新任务各字段详细指南
- [任务进展管理](task-trace.md) - 获取和创建任务进展
- [用户和成员管理](user.md) - 获取用户信息、查询企业成员
- [项目管理](project.md) - 查询项目列表和详情
- [任务 TQL 参考](TQL_REFERENCE.md) - 任务查询语言完整参考
- [最佳实践](BEST_PRACTICES.md) - 使用约束与最佳实践
- [错误处理](ERROR_HANDLING.md) - 常见错误及解决方案
