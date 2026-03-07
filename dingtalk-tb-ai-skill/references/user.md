# 用户和成员管理

本文档介绍如何使用 Teambition API 获取用户信息和查询企业成员。

## 功能列表

- [获取当前用户信息](#获取当前用户信息)
- [查询企业成员](#查询企业成员)

---

## 获取当前用户信息

获取当前用户在企业中的基本成员信息。

### 基本用法

```bash
uv run scripts/get-current-user.py
```

### 返回信息

返回的用户信息包括：

| 字段 | 说明 | 示例 |
|------|------|------|
| `userId` | 用户 ID | `696f2c084a459842b42b035b` |
| `name` | 用户名称 | `张三` |
| `email` | 邮箱地址 | `zhangsan@example.com` |
| `phone` | 手机号码 | `13800138000` |
| `role` | 角色 | `member` / `admin` |
| `isDisabled` | 账号是否禁用 | `false` |
| `employeeNumber` | 工号 | `001` |

### 使用示例

```bash
# 获取当前用户信息
uv run scripts/get-current-user.py
```

### 响应示例

```json
{
  "userId": "696f2c084a459842b42b035b",
  "name": "张三",
  "email": "zhangsan@example.com",
  "phone": "13800138000",
  "role": "member",
  "isDisabled": false,
  "employeeNumber": "001"
}
```

### 常见用途

1. **获取当前用户 ID**：用于构建 TQL 查询时的用户标识
2. **显示用户信息**：在应用中展示当前登录用户的基本信息
3. **权限判断**：根据用户角色进行权限控制

---

## 查询企业成员

根据用户 ID 或搜索关键字查询企业成员信息，支持分页。

### 基本用法

```bash
uv run scripts/query-members.py [选项]
```

### 参数说明

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `--user-ids` | 字符串 | 否 | 用户 ID 集合，逗号分隔 |
| `--query` | 字符串 | 否 | 搜索关键字（匹配工号、姓名、邮箱、手机号） |
| `--page-size` | 整数 | 否 | 每页大小，默认由 API 决定 |
| `--page-token` | 字符串 | 否 | 分页令牌，用于获取下一页 |

**注意**：`--user-ids` 和 `--query` 至少需要提供一个。

### 返回信息

返回的成员信息包括：

| 字段 | 说明 |
|------|------|
| `userId` | 用户 ID |
| `name` | 用户名称 |
| `role` | 角色（member/admin） |
| `isDisabled` | 账号是否禁用 |
| `email` | 邮箱地址 |
| `phone` | 手机号码 |
| `employeeNumber` | 工号 |
| `position` | 职位 |

### 使用示例

#### 1. 根据用户 ID 查询

```bash
# 查询单个用户
uv run scripts/query-members.py --user-ids 696f2c084a459842b42b035b

# 查询多个用户
uv run scripts/query-members.py --user-ids 696f2c084a459842b42b035b,696f2c084a459842b42b035c
```

#### 2. 根据关键字搜索

```bash
# 搜索姓名
uv run scripts/query-members.py --query 张三

# 搜索工号
uv run scripts/query-members.py --query 001

# 搜索邮箱
uv run scripts/query-members.py --query zhangsan@example.com
```

#### 3. 分页查询

```bash
# 设置每页大小
uv run scripts/query-members.py --query 张 --page-size 10

# 获取下一页（使用上一次返回的 nextPageToken）
uv run scripts/query-members.py --query 张 --page-token "next_page_token_here"
```

### 响应示例

```json
{
  "code": 200,
  "result": [
    {
      "userId": "696f2c084a459842b42b035b",
      "name": "张三",
      "role": "member",
      "isDisabled": false,
      "email": "zhangsan@example.com",
      "phone": "13800138000",
      "employeeNumber": "001",
      "position": "工程师"
    }
  ],
  "count": 1,
  "nextPageToken": null
}
```

### 常见用途

1. **ID 转姓名**：将任务、项目中的用户 ID 转换为可读的姓名
2. **成员搜索**：在应用中实现成员搜索功能
3. **批量查询**：一次性获取多个用户的详细信息
4. **通讯录**：构建企业内部通讯录

### 最佳实践

1. **批量查询优化**：如果需要查询多个用户，使用 `--user-ids` 一次性查询，而不是多次单独查询
2. **搜索关键字**：使用 `--query` 时，关键字越精确，返回结果越准确
3. **分页处理**：对于大量数据，使用分页避免一次性加载过多数据
4. **缓存结果**：用户信息变化不频繁，可以适当缓存查询结果

### 注意事项

1. 搜索关键字会匹配工号、姓名、邮箱、手机号等多个字段
2. 查询结果只包含当前企业的成员
3. 需要确保 Token 有查询成员的权限
4. 返回的成员信息可能因权限不同而有所差异

---

## 相关文档

- [项目管理](project.md) - 查询项目列表和详情
- [任务管理](task.md) - 查询任务列表和详情
- [最佳实践](BEST_PRACTICES.md) - 使用约束与最佳实践
- [错误处理](ERROR_HANDLING.md) - 常见错误及解决方案
