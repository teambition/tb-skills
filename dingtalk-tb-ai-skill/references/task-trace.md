# 任务进展管理

本文档介绍如何使用 Teambition API 管理任务进展，包括获取进展列表和创建新进展。

## 📚 目录

- [功能概述](#功能概述)
- [API 接口说明](#api-接口说明)
- [获取任务进展](#获取任务进展)
- [创建任务进展](#创建任务进展)
- [进展状态说明](#进展状态说明)
- [常见问题](#常见问题)

---

## 功能概述

任务进展用于记录任务的执行情况和最新动态，帮助团队成员了解任务的实时状态。

**主要功能：**
- 📋 获取任务的进展列表
- ✍️ 创建新的任务进展
- 🚦 标记进展状态（正常/风险/逾期）
- 👥 提醒相关人员关注进展
- 📎 支持附件（通过 API）

---

## API 接口说明

任务进展功能通过以下两个 API 接口实现，可以直接使用 `call-user-api.py` 调用。

### 1. 获取任务进展

**接口信息：**
- **方法**：GET
- **路径**：`v3/task/{taskId}/traces`
- **参数**：
  - `taskId`（路径参数，必填）：任务 ID
  - `pageSize`（查询参数，可选）：每页大小
  - `pageToken`（查询参数，可选）：分页令牌

### 2. 创建任务进展

**接口信息：**
- **方法**：POST
- **路径**：`v3/task/{taskId}/trace/create`
- **参数**：
  - `taskId`（路径参数，必填）：任务 ID
  - 请求体（JSON）：
    - `title`（必填）：进展标题
    - `content`（可选）：进展内容
    - `status`（可选，默认 1）：进展状态（1=正常，2=风险，3=逾期）
    - `reminderIds`（可选）：提醒人 ID 列表

---

## 获取任务进展

获取指定任务的进展列表，支持分页查询。

### 基本用法

```bash
uv run scripts/call-user-api.py GET "v3/task/<任务ID>/traces"
```

### 使用示例

#### 1. 基本查询

```bash
# 获取任务的所有进展
uv run scripts/call-user-api.py GET "v3/task/67ec9b8c3c6130ac88605c3e/traces"
```

#### 2. 分页查询

```bash
# 设置每页大小
uv run scripts/call-user-api.py GET "v3/task/67ec9b8c3c6130ac88605c3e/traces?pageSize=20"

# 使用分页令牌获取下一页
uv run scripts/call-user-api.py GET "v3/task/67ec9b8c3c6130ac88605c3e/traces?pageToken=next_page_token_here"
```

### 响应格式

```json
{
  "totalCount": 10,
  "nextPageToken": "next_page_token_here",
  "result": [
    {
      "id": "67ec9b8c3c6130ac88605c50",
      "title": "完成需求分析",
      "content": "已完成需求文档编写和评审",
      "status": 1,
      "creatorId": "696f2c084a459842b42b035b",
      "created": "2026-02-27T10:00:00.000Z",
      "updated": "2026-02-27T10:00:00.000Z",
      "attachments": []
    }
  ]
}
```

### 返回字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 进展 ID |
| `title` | string | 进展标题 |
| `content` | string | 进展内容 |
| `status` | integer | 进展状态（1=正常, 2=风险, 3=逾期） |
| `creatorId` | string | 创建人 ID |
| `created` | string | 创建时间 |
| `updated` | string | 更新时间 |
| `attachments` | array | 附件列表 |
| `reminderIds` | array | 提醒人 ID 列表 |

---

## 创建任务进展

为任务创建新的进展记录。

### 基本用法

```bash
uv run scripts/call-user-api.py POST "v3/task/<任务ID>/trace/create" '<JSON数据>'
```

### 使用示例

#### 1. 创建简单进展

```bash
# 只提供标题
uv run scripts/call-user-api.py POST "v3/task/67ec9b8c3c6130ac88605c3e/trace/create" \
  '{"title":"完成需求分析","content":""}'
```

#### 2. 创建详细进展

```bash
# 包含内容
uv run scripts/call-user-api.py POST "v3/task/67ec9b8c3c6130ac88605c3e/trace/create" \
  '{"title":"完成开发","content":"已完成核心功能开发，正在进行单元测试"}'
```

#### 3. 标记风险进展

```bash
# 状态为"存在风险"（status=2）
uv run scripts/call-user-api.py POST "v3/task/67ec9b8c3c6130ac88605c3e/trace/create" \
  '{"title":"遇到技术难题","content":"第三方接口不稳定，需要寻找替代方案","status":2}'
```

#### 4. 标记逾期进展

```bash
# 状态为"逾期"（status=3）
uv run scripts/call-user-api.py POST "v3/task/67ec9b8c3c6130ac88605c3e/trace/create" \
  '{"title":"进度延期","content":"因需求变更导致延期，预计延期3天","status":3}'
```

#### 5. 提醒相关人员

```bash
# 创建进展并提醒相关人员
uv run scripts/call-user-api.py POST "v3/task/67ec9b8c3c6130ac88605c3e/trace/create" \
  '{"title":"需要评审","content":"代码已提交，请评审","reminderIds":["696f2c084a459842b42b035b","696f2c084a459842b42b035c"]}'
```

### 响应格式

```json
{
  "id": "67ec9b8c3c6130ac88605c50",
  "title": "完成需求分析",
  "content": "已完成需求文档编写和评审",
  "status": 1,
  "creatorId": "696f2c084a459842b42b035b",
  "created": "2026-02-27T10:00:00.000Z",
  "updated": "2026-02-27T10:00:00.000Z"
}
```

---

## 进展状态说明

任务进展支持三种状态，用于标识任务的当前情况：

| 状态值 | 状态名称 | 说明 | 使用场景 |
|--------|---------|------|---------|
| 1 | 正常 | 任务进展顺利 | 按计划完成阶段性工作 |
| 2 | 存在风险 | 任务遇到问题或风险 | 遇到技术难题、资源不足等 |
| 3 | 逾期 | 任务进度延期 | 超出预期时间、需要调整计划 |

### 状态使用建议

**正常状态（1）**
- 按计划完成阶段性目标
- 日常进度更新
- 里程碑达成

**风险状态（2）**
- 遇到技术难题
- 依赖项延期
- 资源不足
- 需求变更

**逾期状态（3）**
- 超出预期时间
- 需要调整计划
- 影响整体进度

---

## 常见问题

### 1. 如何获取任务 ID？

**方法 1：查询任务列表**
```bash
uv run scripts/query-tasks.py --tql "executorId = me() AND isDone = false"
```

**方法 2：查询任务详情**
```bash
uv run scripts/query-tasks-detail.py <任务ID>
```

### 2. 进展标题和内容有什么区别？

- **标题**：简短概括，必填，用于快速了解进展要点
- **内容**：详细描述，可选，用于记录具体情况和细节

**示例：**
- 标题：`完成需求分析`
- 内容：`已完成需求文档编写，包括功能需求、非功能需求和用例设计。文档已通过产品经理和技术负责人评审。`

### 3. 如何获取用户 ID 用于提醒？

**查询成员**
```bash
uv run scripts/query-members.py --keyword '张三'
```

**获取当前用户**
```bash
uv run scripts/get-current-user.py
```

### 4. 可以修改已创建的进展吗？

根据 API 文档，创建进展接口用于"创建/更新任务的最新进展"。如需修改，可以创建新的进展记录。

### 5. 进展列表是按什么顺序排列的？

默认按创建时间倒序排列，最新的进展在前。

### 6. 如何查看进展的附件？

附件信息包含在进展详情的 `attachments` 字段中，包括：
- `id`：文件 ID
- `fileName`：文件名称
- `fileType`：文件类型
- `fileSize`：文件大小
- `downloadUrl`：下载地址
- `thumbnailUrl`：预览地址

### 7. 提醒人会收到什么通知？

提醒人会在 Teambition 中收到进展通知，提醒他们关注该任务的最新进展。

### 8. 进展状态会影响任务状态吗？

进展状态是独立的，不会直接影响任务状态。但可以作为任务状态的参考依据。

### 9. 可以删除进展吗？

进展有 `isDeleted` 字段，但当前脚本不支持删除操作。如需删除，请使用 Teambition 界面操作。

### 10. 如何批量创建进展？

可以编写脚本循环调用 `call-user-api.py`，或使用 Python 直接调用 API。

---

## 最佳实践

### 1. 定期更新进展

建议在以下时机更新任务进展：
- 完成阶段性工作
- 遇到问题或风险
- 每日/每周例行更新
- 里程碑达成

### 2. 清晰的标题

进展标题应该：
- 简洁明了（建议 10-20 字）
- 突出重点
- 使用动词开头（如：完成、开始、遇到）

**好的示例：**
- ✅ `完成数据库设计`
- ✅ `开始前端开发`
- ✅ `遇到性能问题`

**不好的示例：**
- ❌ `今天的工作`
- ❌ `更新`
- ❌ `进展`

### 3. 详细的内容

进展内容应该包含：
- 具体完成了什么
- 遇到了什么问题
- 下一步计划
- 需要的支持

### 4. 合理使用状态

- 不要过度使用风险和逾期状态
- 及时更新状态变化
- 风险和逾期进展应说明原因和解决方案

### 5. 及时提醒相关人员

在以下情况使用提醒功能：
- 需要他人协助
- 需要评审或确认
- 影响他人工作
- 重要里程碑达成

---

## 相关文档

- [任务管理](task.md) - 查询任务列表和详情
- [用户和成员管理](user.md) - 获取用户信息、查询企业成员
- [项目管理](project.md) - 查询项目列表和详情
- [最佳实践](BEST_PRACTICES.md) - 使用约束与最佳实践
- [错误处理](ERROR_HANDLING.md) - 常见错误及解决方案
