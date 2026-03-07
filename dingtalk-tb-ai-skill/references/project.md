# 项目管理

本文档介绍如何使用 Teambition API 查询项目列表和项目详情。

## ⚠️ 重要约束

在进行项目相关操作时，请遵守以下约束：

1. **优先使用文档提供的方式和脚本**：查询项目、查询项目详情等操作时，优先使用本文档中已提供的方式和脚本，而不是直接调用底层 API。文档中的脚本已经过充分测试和优化，能够提供更好的用户体验和错误处理。

2. **TQL 查询参考规范**：当需要编写 TQL 查询语句时，必须参考本文档中的示例。如果本文档中未找到相应的示例，必须参考 [项目 TQL 参考文档](PROJECT_TQL_REFERENCE.md)，**严禁编造或猜测 TQL 语法**。

## 功能列表

- [查询项目列表](#查询项目列表)
- [查询项目详情](#查询项目详情)

---

## 查询项目列表

使用 TQL（项目查询语言）查询 Teambition 项目，支持分页，默认自动获取简单详情。

### 基本用法

```bash
uv run scripts/query-projects.py [选项]
```

### 参数说明

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

**完整 TQL 参考**：请查看 [项目 TQL 参考文档](PROJECT_TQL_REFERENCE.md)

**注意**：项目没有截止时间（dueDate）字段，只有创建时间（created）和更新时间（updated）。如需查询任务的截止时间，请参考 [任务管理文档](task.md)。

### 使用示例

#### 1. 基本查询

```bash
# 查询所有项目（自动获取简单详情）
uv run scripts/query-projects.py

# 只获取项目 ID 列表，不获取详情
uv run scripts/query-projects.py --no-details
```

#### 2. 使用 TQL 筛选

```bash
# 查询我创建的项目
uv run scripts/query-projects.py --tql "creatorId = me()"

# 查询我参与的项目
uv run scripts/query-projects.py --tql "involveMembers = me()"

# 按名称搜索
uv run scripts/query-projects.py --tql "nameText ~ '测试'"

# 查询已归档的项目
uv run scripts/query-projects.py --tql "isSuspended = true"
```

#### 3. 时间范围查询

```bash
# 查询今天创建的项目
uv run scripts/query-projects.py --tql "created <= endOf(d) AND created >= startOf(d)"

# 查询本周创建的项目
uv run scripts/query-projects.py --tql "created <= endOf(w) AND created >= startOf(w)"

# 查询本月创建的项目
uv run scripts/query-projects.py --tql "created <= endOf(M) AND created >= startOf(M)"

# 查询最近7天创建的项目
uv run scripts/query-projects.py --tql "created <= endOf(d, -1d) AND created >= startOf(d, -7d)"

# 查询指定日期之后创建的项目
uv run scripts/query-projects.py --tql "created >= '2026-03-01T00:00:00.000Z'"

# 查询指定日期范围内创建的项目
uv run scripts/query-projects.py --tql "created >= '2026-03-01T00:00:00.000Z' AND created <= '2026-03-31T23:59:59.999Z'"

# 查询今天更新的项目
uv run scripts/query-projects.py --tql "updated <= endOf(d) AND updated >= startOf(d)"
```

#### 4. 组合查询

```bash
# 查询我创建的且未归档的项目
uv run scripts/query-projects.py --tql "creatorId = me() AND isSuspended = false"

# 查询最近7天创建的项目，按更新时间降序
uv run scripts/query-projects.py --tql "created <= endOf(d, -1d) AND created >= startOf(d, -7d) ORDER BY updated DESC"

# 查询本月创建且我参与的项目
uv run scripts/query-projects.py --tql "created >= startOf(M) AND involveMembers = me()"
```

#### 5. 分页查询

```bash
# 设置每页大小
uv run scripts/query-projects.py --page-size 20

# 获取下一页
uv run scripts/query-projects.py --page-token "next_page_token_here"
```

#### 6. 包含模板项目

```bash
# 查询包括模板在内的所有项目
uv run scripts/query-projects.py --include-template
```

### 响应格式

查询项目列表会返回项目 ID 列表，默认情况下会自动调用详情接口获取每个项目的简单信息。

```json
{
  "code": 200,
  "result": [
    "67ec9b8c3c6130ac88605c3e",
    "67ec9b8c3c6130ac88605c3f"
  ],
  "count": 2,
  "nextPageToken": null
}
```

### 注意事项

1. **默认排除模板**：默认会自动排除模板项目（`isTemplate = false`），避免查询到模板
2. **自动获取详情**：默认会自动调用详情接口获取项目的简单信息，方便直接使用
3. **TQL 语法**：查询"我"相关的内容时，必须使用 `me()` 函数而不是具体的用户 ID
4. **分页处理**：大量数据时建议使用分页功能

---

## 查询项目详情

根据项目 ID 查询项目的详细信息，支持简单和详细两种信息级别。

### 基本用法

```bash
uv run scripts/query-projects-detail.py <项目ID> [选项]
```

### 参数说明

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `项目ID` | 字符串 | 是 | 项目 ID 集合，使用逗号分隔 |
| `--detail-level` | 字符串 | 否 | 详细程度：`simple`（默认）或 `detailed` |
| `--extra-fields` | 字符串 | 否 | 简单模式下额外包含的字段，逗号分隔 |

### 信息级别

#### 简单信息（simple）

默认包含的字段：

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

#### 详细信息（detailed）

包含所有 API 返回的字段（20+ 个字段），包括：
- 所有简单信息字段
- `logo`：项目 LOGO
- `organizationId`：企业 ID
- `uniqueIdPrefix`：任务 ID 前缀
- `startDate`：项目开始时间
- `endDate`：项目结束时间
- `suspendedAt`：归档时间
- 自定义字段等

### 使用示例

#### 1. 查询简单信息

```bash
# 查询单个项目
uv run scripts/query-projects-detail.py 67ec9b8c3c6130ac88605c3e

# 查询多个项目
uv run scripts/query-projects-detail.py 67ec9b8c3c6130ac88605c3e,67ec9b8c3c6130ac88605c3f
```

#### 2. 追加额外字段

```bash
# 简单模式追加 logo 和任务前缀
uv run scripts/query-projects-detail.py 67ec9b8c3c6130ac88605c3e --extra-fields logo,uniqueIdPrefix

# 追加多个字段
uv run scripts/query-projects-detail.py 67ec9b8c3c6130ac88605c3e --extra-fields logo,organizationId,startDate,endDate
```

#### 3. 查询详细信息

```bash
# 查询单个项目的完整信息
uv run scripts/query-projects-detail.py 67ec9b8c3c6130ac88605c3e --detail-level detailed

# 查询多个项目的完整信息
uv run scripts/query-projects-detail.py 67ec9b8c3c6130ac88605c3e,67ec9b8c3c6130ac88605c3f --detail-level detailed
```

### 响应示例

#### 简单信息响应

```json
{
  "code": 200,
  "result": [
    {
      "id": "67ec9b8c3c6130ac88605c3e",
      "name": "测试项目",
      "description": "这是一个测试项目",
      "visibility": "public",
      "isTemplate": false,
      "creatorId": "696f2c084a459842b42b035b",
      "isArchived": false,
      "isSuspended": false,
      "created": "2024-01-01T00:00:00.000Z",
      "updated": "2024-01-10T00:00:00.000Z"
    }
  ]
}
```

### 常见用途

1. **项目概览**：获取项目的基本信息用于展示
2. **项目管理**：查看项目状态、归档情况等
3. **批量查询**：一次性获取多个项目的详细信息
4. **数据分析**：收集项目数据进行统计分析

### 最佳实践

1. **按需获取**：默认使用简单模式，只有需要时才使用详细模式
2. **批量查询**：需要查询多个项目时，使用逗号分隔一次性查询
3. **额外字段**：使用 `--extra-fields` 精确控制需要的字段，避免获取不必要的数据
4. **缓存结果**：项目信息变化不频繁，可以适当缓存查询结果

### 注意事项

1. 项目 ID 必须是有效的 MongoDB ObjectId 格式
2. 查询不存在的项目 ID 不会报错，只是结果中不包含该项目
3. 详细模式返回的字段可能因项目配置不同而有所差异
4. 自定义字段在详细模式下才会返回

---

## 相关文档

- [用户和成员管理](user.md) - 获取用户信息、查询企业成员
- [任务管理](task.md) - 查询任务列表和详情
- [项目 TQL 参考](PROJECT_TQL_REFERENCE.md) - 项目查询语言完整参考
- [最佳实践](BEST_PRACTICES.md) - 使用约束与最佳实践
- [错误处理](ERROR_HANDLING.md) - 常见错误及解决方案
