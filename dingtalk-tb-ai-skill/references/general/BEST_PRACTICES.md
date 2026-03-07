# 使用约束与最佳实践

本文档介绍使用 Teambition API 技能时的最佳实践和注意事项。

## 目录

- [信息展示原则](#信息展示原则)
- [TQL 查询最佳实践](#tql-查询最佳实践)
- [性能优化](#性能优化)
- [安全注意事项](#安全注意事项)
- [其他注意事项](#其他注意事项)

---

## 信息展示原则

**重要**：在使用本技能时，请遵循以下原则以提供更好的用户体验。

### 1. 避免展示技术 ID

除非用户明确要求，否则尽量不要直接展示以下技术性 ID 字段：

❌ **不推荐的展示方式**：
```
任务执行人：executorId: 5f9a1b2c3d4e5f6g7h8i9j0k
项目 ID：projectId: 67ec9b8c3c6130ac88605c3e
```

✅ **推荐的展示方式**：
```
任务执行人：张三
项目名称：测试项目
```

**需要转换的 ID 字段**：
- `executorId`：执行人 ID → 执行人姓名
- `creatorId`：创建人 ID → 创建人姓名
- `projectId`：项目 ID → 项目名称
- `sprintId`：迭代 ID → 迭代名称
- `stageId`：任务列 ID → 任务列名称

**如何转换**：
1. 使用 `query-members.py` 将用户 ID 转换为姓名
2. 使用 `query-projects-detail.py` 将项目 ID 转换为项目名称
3. 批量查询时使用逗号分隔的 ID 列表，提高效率

### 2. 优先展示可读信息

✅ **推荐展示的字段**：

**任务信息**：
- `content`：任务标题
- `isDone`：完成状态（已完成/未完成）
- `dueDate`：截止时间
- `priority`：优先级（紧急/高/中/低）
- `created`：创建时间
- `updated`：更新时间

**项目信息**：
- `name`：项目名称
- `description`：项目描述
- `visibility`：可见性（公开/私有）
- `isSuspended`：归档状态
- `created`：创建时间
- `updated`：更新时间

### 3. 按需获取详细信息

**默认策略**：
- 使用简单模式（`simple`），只展示核心字段
- 避免一次性加载过多不必要的数据

**追加字段**：
- 如果用户需要更多信息，使用 `--extra-fields` 追加特定字段
- 例如：`--extra-fields note,sprintId,stageId`

**详细模式**：
- 只有在用户明确要求"完整信息"或"所有字段"时才使用 `detailed` 模式
- 详细模式会返回 20-30+ 个字段，包括自定义字段

---

## TQL 查询最佳实践

### 1. 使用 me() 函数

查询"我"相关的内容时，**必须**使用 `me()` 函数而不是具体的用户 ID。

✅ **正确**：
```bash
# 我的待办任务
--tql "executorId = me() AND isDone = false"

# 我创建的项目
--tql "creatorId = me()"
```

❌ **错误**：
```bash
# 不要使用具体的用户 ID
--tql "executorId = '696f2c084a459842b42b035b' AND isDone = false"
```

**原因**：
- `me()` 函数会自动获取当前用户的 ID
- 避免硬编码用户 ID，提高代码的可维护性
- 支持多用户场景，不同用户使用相同的查询语句

### 2. 时间查询

使用 `startOf()` 和 `endOf()` 函数处理相对时间。

**常用时间查询**：

```bash
# 今天
dueDate <= endOf(d) AND dueDate >= startOf(d)

# 本周
dueDate <= endOf(w) AND dueDate >= startOf(w)

# 本月
dueDate <= endOf(M) AND dueDate >= startOf(M)

# 过去7天
created <= endOf(d, -1d) AND created >= startOf(d, -7d)

# 未来3天
dueDate <= endOf(d, 3d) AND dueDate >= startOf(d)
```

**时间单位**：
- `d`：天（day）
- `w`：周（week）
- `M`：月（month）
- `y`：年（year）

### 3. 排序

添加 `ORDER BY` 提升查询结果的可用性。

**常用排序**：

```bash
# 按更新时间降序（最新的在前）
ORDER BY updated DESC

# 按创建时间升序（最早的在前）
ORDER BY created ASC

# 按截止时间升序（最早到期的在前）
ORDER BY dueDate ASC

# 按优先级升序（紧急的在前）
ORDER BY priority ASC
```

**多字段排序**：
```bash
# 先按优先级，再按截止时间
ORDER BY priority ASC, dueDate ASC
```

### 4. 组合查询

使用 `AND`、`OR` 组合多个条件。

**示例**：

```bash
# 我的高优先级待办任务
executorId = me() AND isDone = false AND priority <= 1

# 今天或明天到期的任务
dueDate <= endOf(d, 1d) AND dueDate >= startOf(d)

# 某个项目的待办任务
projectId = '67ec9b8c3c6130ac88605c3e' AND isDone = false
```

### 5. 文本搜索

使用 `~` 进行模糊匹配。

```bash
# 按名称搜索项目
nameText ~ '测试'

# 按内容搜索任务
content ~ '需求'
```

---

## 性能优化

### 1. 批量查询

需要查询多个对象时，使用批量查询而不是多次单独查询。

✅ **推荐**：
```bash
# 一次查询多个任务
uv run scripts/query-tasks-detail.py task1,task2,task3

# 一次查询多个用户
uv run scripts/query-members.py --user-ids user1,user2,user3
```

❌ **不推荐**：
```bash
# 多次单独查询
uv run scripts/query-tasks-detail.py task1
uv run scripts/query-tasks-detail.py task2
uv run scripts/query-tasks-detail.py task3
```

### 2. 使用分页

大量数据时使用分页功能，避免一次性查询过多数据。

```bash
# 设置合理的分页大小
uv run scripts/query-tasks.py --page-size 50

# 使用 nextPageToken 获取下一页
uv run scripts/query-tasks.py --page-token "next_page_token_here"
```

**建议的分页大小**：
- 列表展示：20-50 条
- 数据导出：100-200 条
- 避免超过 500 条

### 3. 按需获取字段

使用简单模式和 `--extra-fields`，只获取需要的字段。

```bash
# 只获取核心字段
uv run scripts/query-tasks-detail.py task_id

# 追加特定字段
uv run scripts/query-tasks-detail.py task_id --extra-fields note,sprintId
```

### 4. 缓存结果

对于变化不频繁的数据，可以适当缓存查询结果。

**适合缓存的数据**：
- 用户信息（姓名、邮箱等）
- 项目基本信息
- 企业成员列表

**不适合缓存的数据**：
- 任务状态（isDone）
- 任务进度（progress）
- 实时统计数据

---

## 安全注意事项

### 1. Token 安全

**重要**：User Token 是敏感信息，请妥善保管。

✅ **推荐做法**：
- 使用环境变量存储 Token
- 使用配置文件存储 Token，并将配置文件加入 `.gitignore`
- 定期更换 Token

❌ **禁止行为**：
- 不要将 Token 硬编码在代码中
- 不要将 Token 提交到公共代码仓库
- 不要在日志中打印 Token

### 2. 权限管理

确保 User Token 具有相应的权限。

**所需权限**：
- 查询任务：需要任务读取权限
- 查询项目：需要项目读取权限
- 查询成员：需要成员读取权限

**权限不足时的表现**：
- API 返回 403 错误
- 某些字段返回空值
- 查询结果为空

### 3. 数据隐私

注意保护用户隐私数据。

**敏感信息**：
- 用户手机号
- 用户邮箱
- 任务备注中的敏感内容

**处理建议**：
- 只在必要时获取敏感信息
- 不要将敏感信息记录到日志
- 遵守企业的数据安全规范

---

## 其他注意事项

### 1. 网络连接

确保网络连接正常，能够访问 Teambition API。

**API 地址**：
- 生产环境：`https://open.teambition.com`
- 需要稳定的网络连接
- 建议配置超时时间（30-60 秒）

### 2. 错误处理

正确处理 API 错误，提供友好的错误提示。

**常见错误**：
- 401：认证失败，检查 Token
- 403：权限不足，检查权限配置
- 400：参数错误，检查 TQL 语法
- 500：服务器错误，稍后重试

详细的错误处理请参考：[错误处理文档](ERROR_HANDLING.md)

### 3. API 限流

注意 API 调用频率限制。

**建议**：
- 避免短时间内大量调用
- 使用批量查询减少调用次数
- 合理使用缓存
- 必要时添加延迟

### 4. 数据一致性

注意数据的一致性问题。

**场景**：
- 查询任务列表后，任务可能被删除或修改
- 查询详情时，数据可能已经过期

**建议**：
- 查询详情时检查返回结果
- 处理数据不存在的情况
- 必要时重新查询最新数据

---

## 相关文档

- [用户和成员管理](user.md) - 获取用户信息、查询企业成员
- [项目管理](project.md) - 查询项目列表和详情
- [任务管理](task.md) - 查询任务列表和详情
- [任务 TQL 参考](TQL_REFERENCE.md) - 任务查询语言完整参考
- [项目 TQL 参考](PROJECT_TQL_REFERENCE.md) - 项目查询语言完整参考
- [错误处理](ERROR_HANDLING.md) - 常见错误及解决方案
