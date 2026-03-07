# 优先级管理

本文档介绍如何使用 Teambition API 查询和更新任务优先级。

## 功能列表

- [查询企业优先级配置](#查询企业优先级配置)
- [更新任务优先级](#更新任务优先级)
- [优先级使用说明](#优先级使用说明)

---

## 查询企业优先级配置

获取企业配置的任务优先级列表。不同企业可能有不同的优先级配置，需要先查询再使用。
组织/企业id可通过 `uv run scripts/query-projects-detail.py <项目ID> --detail-level detailed` 查询

### 快速开始

```bash
uv run scripts/get-priority-list.py <组织ID>
```

### 脚本说明

**脚本路径**：`scripts/get-priority-list.py`

**接口信息**：
- **方法**：GET
- **路径**：`/v3/project/priority/list`
- **参数**：
  - `organizationId`（必填）：企业/组织 ID

### 参数说明

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| 组织ID | string | 是 | Teambition 企业/组织 ID |

### 使用示例

```bash
# 查询企业优先级配置
uv run scripts/get-priority-list.py 67ec9b8c3c6130ac88605c3e
```

### 输出说明

脚本会输出表格形式的优先级列表和完整的 JSON 数据：
### 获取组织 ID

组织 ID 可以从项目信息中获取：
1. 使用 `query-projects-detail.py` 脚本查询项目详情
2. 在返回的数据中找到 `organizationId` 字段

---

## 更新任务优先级

更新指定任务的优先级。

### 快速开始

```bash
uv run scripts/user-update-task-priority.py <任务ID> <优先级>
```

### 脚本说明

**脚本路径**：`scripts/user-update-task-priority.py`

**接口信息**：
- **方法**：PUT
- **路径**：`/v3/task/{taskId}/priority`
- **参数**：
  - `taskId`（路径参数，必填）：任务 ID
  - 请求体（JSON）：
    - `priority`（必填）：优先级值（整数）

### 参数说明

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| 任务ID | string | 是 | Teambition 任务 ID |
| 优先级 | integer | 是 | 优先级值（整数） |

### 使用示例

```bash
# 更新任务优先级
uv run scripts/user-update-task-priority.py 69a13167f367e8c8a5e70d39 3
```

### 注意事项

1. 企业可以自定义优先级映射，直接传入对应的优先级数值即可
2. 更新前建议先查询企业优先级配置，确认可用的优先级值
3. 优先级值通常是整数，具体含义由企业自定义

---

## 优先级使用说明

### 工作流程

推荐的优先级使用流程：

1. **查询企业配置**：使用 `get-priority-list.py` 脚本获取企业优先级配置
2. **选择合适的优先级值**：根据企业配置选择合适的优先级值
3. **更新任务优先级**：使用 `user-update-task-priority.py` 脚本更新任务优先级

### 示例流程

```bash
# 步骤1: 先查询企业优先级配置，确认可用的优先级值
uv run scripts/get-priority-list.py 67ec9b8c3c6130ac88605c3e

# 步骤2: 更新任务优先级
uv run scripts/user-update-task-priority.py 69a13167f367e8c8a5e70d39 3
```

### 企业自定义优先级

不同企业可以有不同的优先级配置：
- 优先级的数量可以不同
- 优先级的名称可以自定义
- 优先级的值可以重新映射
- 可以设置默认优先级选项

### 最佳实践

1. **总是先查询配置**：在更新优先级前，先使用 `get-priority-list.py` 查询企业配置
2. **使用有效值**：确保传递的优先级值在企业配置范围内
3. **处理错误响应**：注意检查 API 返回的状态码和错误信息
4. **记录默认选项**：了解企业的默认优先级设置

---

## 相关文档

- [任务管理](task.md) - 查询任务列表和详情
- [项目管理](project.md) - 查询项目列表和详情
- [用户和成员管理](user.md) - 获取用户信息、查询企业成员
- [任务 TQL 参考](TQL_REFERENCE.md) - 任务查询语言完整参考
- [最佳实践](BEST_PRACTICES.md) - 使用约束与最佳实践
- [错误处理](ERROR_HANDLING.md) - 常见错误及解决方案