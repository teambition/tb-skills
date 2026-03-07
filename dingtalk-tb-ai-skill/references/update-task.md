# 更新任务

本文档介绍如何使用 `update-task.py` 脚本更新 Teambition 任务，重点说明使用方式和示例。

## 快速开始

### 基本用法

```bash
uv run scripts/update-task.py --task-id <任务ID> [更新字段选项]
```

### 最简单的更新

```bash
# 更新任务标题
uv run scripts/update-task.py \
  --task-id '67f0a1b2c3d4e5f6g7h8i9j0' \
  --content '新的任务标题'
```

### 更新多个字段（并行执行）

```bash
uv run scripts/update-task.py \
  --task-id '67f0a1b2c3d4e5f6g7h8i9j0' \
  --content '更新后的标题' \
  --executor-id '696f2c084a459842b42b035b' \
  --due-date '2026-03-15T00:00:00.000Z' \
  --priority 1 \
  --note '更新后的备注'
```

---

## 支持的更新字段

| 参数 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| `--task-id` | string | **必填** 任务 ID | `'67f0a1b2c3d4e5f6g7h8i9j0'` |
| `--content` | string | 任务标题 | `'新的任务标题'` |
| `--executor-id` | string | 执行人 ID | `'696f2c084a459842b42b035b'` |
| `--due-date` | string | 截止日期（ISO 8601） | `'2026-03-15T00:00:00.000Z'` |
| `--start-date` | string | 开始日期（ISO 8601） | `'2026-03-01T00:00:00.000Z'` |
| `--note` | string | 任务备注 | `'更新后的备注'` |
| `--priority` | integer | 优先级（0=低，1=中，2=高，3=紧急） | `1` |
| `--story-point` | string | 故事点 | `'8'` |
| `--taskflowstatus-id` | string | 任务状态 ID | `'67ec9b8c3c6130ac88605c45'` |
| `--involve-members` | JSON | 参与者列表（完全替换） | `'["user1","user2"]'` |
| `--add-involvers` | JSON | 新增参与者 | `'["user3"]'` |
| `--del-involvers` | JSON | 移除参与者 | `'["user4"]'` |
| `--customfields` | JSON | 自定义字段 | 见下方示例 |

**重要特性**：
- ✅ **并行执行**：多个字段同时更新，显著提升性能
- ✅ **增量更新**：只修改指定字段，不影响其他字段
- ✅ **独立端点**：每个字段通过独立 API 更新

---

## 常用字段获取方式

### 获取任务 ID

```bash
# 查询我的待办任务
uv run scripts/query-tasks.py --tql "executorId = me() AND isDone = false"

# 通过标题搜索
uv run scripts/query-tasks.py --tql "content ~ '任务标题关键词'"
```

### 获取用户 ID

```bash
# 查询成员
uv run scripts/query-members.py --keyword '张三'

# 获取当前用户
uv run scripts/get-current-user.py
```

### 获取任务状态 ID

```bash
# 获取项目的所有工作流状态
uv run scripts/get-taskflow-statuses.py '项目ID'

# 根据名称搜索状态
uv run scripts/get-taskflow-statuses.py '项目ID' --q '进行中'
```

### 获取自定义字段配置

```bash
# 获取项目的所有自定义字段
uv run scripts/get-custom-fields.py '项目ID'

# 获取特定任务类型的自定义字段
uv run scripts/get-custom-fields.py '项目ID' --sfc-id '任务类型ID'
```

---

## 使用示例

### 1. 更新单个字段

```bash
# 更新任务标题
uv run scripts/update-task.py \
  --task-id '67f0a1b2c3d4e5f6g7h8i9j0' \
  --content '新的任务标题'

# 更新执行人
uv run scripts/update-task.py \
  --task-id '67f0a1b2c3d4e5f6g7h8i9j0' \
  --executor-id '696f2c084a459842b42b035b'

# 更新截止日期
uv run scripts/update-task.py \
  --task-id '67f0a1b2c3d4e5f6g7h8i9j0' \
  --due-date '2026-03-20T23:59:59.999Z'

# 更新优先级
uv run scripts/update-task.py \
  --task-id '67f0a1b2c3d4e5f6g7h8i9j0' \
  --priority 1

# 更新任务状态
uv run scripts/update-task.py \
  --task-id '67f0a1b2c3d4e5f6g7h8i9j0' \
  --taskflowstatus-id '67ec9b8c3c6130ac88605c45'
```

### 2. 更新参与者

```bash
# 完全替换参与者列表
uv run scripts/update-task.py \
  --task-id '67f0a1b2c3d4e5f6g7h8i9j0' \
  --involve-members '["696f2c084a459842b42b035b", "696f2c084a459842b42b035c"]'

# 增量添加参与者
uv run scripts/update-task.py \
  --task-id '67f0a1b2c3d4e5f6g7h8i9j0' \
  --add-involvers '["696f2c084a459842b42b035d"]'

# 增量移除参与者
uv run scripts/update-task.py \
  --task-id '67f0a1b2c3d4e5f6g7h8i9j0' \
  --del-involvers '["696f2c084a459842b42b035e"]'

# 同时添加和移除
uv run scripts/update-task.py \
  --task-id '67f0a1b2c3d4e5f6g7h8i9j0' \
  --add-involvers '["696f2c084a459842b42b035c"]' \
  --del-involvers '["696f2c084a459842b42b035e"]'
```

### 3. 更新多个字段（并行执行）

```bash
uv run scripts/update-task.py \
  --task-id '67f0a1b2c3d4e5f6g7h8i9j0' \
  --content '更新后的标题' \
  --executor-id '696f2c084a459842b42b035b' \
  --due-date '2026-03-15T23:59:59.999Z' \
  --priority 1 \
  --note '更新后的备注' \
  --story-point '8'
```

**性能优势**：6 个字段并行更新约 1 秒，串行需要约 6 秒

### 4. 更新自定义字段

```bash
# 单选字段
uv run scripts/update-task.py \
  --task-id '67f0a1b2c3d4e5f6g7h8i9j0' \
  --customfields '[{"customfieldId":"67ec9b8c3c6130ac88605c49","value":[{"id":"67ec9b8c3c6130ac88605c4a","title":"功能需求"}]}]'

# 文本字段
uv run scripts/update-task.py \
  --task-id '67f0a1b2c3d4e5f6g7h8i9j0' \
  --customfields '[{"customfieldId":"67ec9b8c3c6130ac88605c4f","value":[{"id":"","title":"这是文本内容"}]}]'

# 多个自定义字段
uv run scripts/update-task.py \
  --task-id '67f0a1b2c3d4e5f6g7h8i9j0' \
  --customfields '[
    {"customfieldId":"67ec9b8c3c6130ac88605c49","value":[{"id":"67ec9b8c3c6130ac88605c4a","title":"功能需求"}]},
    {"customfieldId":"67ec9b8c3c6130ac88605c4f","value":[{"id":"","title":"备注信息"}]}
  ]'
```

---

## 自定义字段类型示例

### ⚠️ 重要提示：字段名称差异

**查询和更新使用不同的字段名称：**

| 场景 | 字段 ID 名称 | 类型字段 | 示例 |
|------|-------------|---------|------|
| **查询任务时** | `cfId` | 包含 `type` | `{"cfId":"xxx","type":"date","value":[...]}` |
| **更新任务时** | `customfieldId` | 不需要 `type` | `{"customfieldId":"xxx","value":[...]}` |

**常见错误：**
```bash
# ❌ 错误：使用查询返回的字段名
--customfields '[{"cfId":"69a2d09e9b95f60686d6bffb","type":"date","value":[...]}]'

# ✅ 正确：使用更新 API 要求的字段名
--customfields '[{"customfieldId":"69a2d09e9b95f60686d6bffb","value":[...]}]'
```

**关键区别：**
1. 更新时使用 `customfieldId` 而不是 `cfId`
2. 更新时不需要 `type` 字段
3. `value` 数组中的对象必须包含 `id` 字段（即使为空字符串）

---

### 单选字段（select）
```json
{"customfieldId":"字段ID","value":[{"id":"选项ID","title":"选项名称"}]}
```

### 多选字段（multiselect）
```json
{"customfieldId":"字段ID","value":[{"id":"选项ID1","title":"选项1"},{"id":"选项ID2","title":"选项2"}]}
```

### 文本字段（text）
```json
{"customfieldId":"字段ID","value":[{"id":"","title":"文本内容"}]}
```

### 数字字段（number）
```json
{"customfieldId":"字段ID","value":[{"id":"","title":"100"}]}
```

### 日期字段（date）
```json
{"customfieldId":"字段ID","value":[{"id":"","title":"2026-03-15T00:00:00.000Z"}]}
```

### 成员字段（member）
```json
{"customfieldId":"字段ID","value":[{"id":"用户ID","title":"用户ID"}]}
```

### 文件字段（file/work）
```json
{"customfieldId":"字段ID","value":[{"id":"","title":"文件名称","metaString":"{\"fileToken\":\"文件Token\"}"}]}
```

**说明**：
- `title`：文件名称
- `metaString`：包含 fileToken 的 JSON 字符串
- `fileToken`：通过文件上传接口获取的 token

**示例**：
```bash
# 先上传文件获取 fileToken
uv run scripts/simple-upload.py \
  --file-path '/path/to/document.pdf' \
  --scope 'task:任务ID' \
  --category 'attachment'

# 使用获取的 fileToken 更新自定义字段
uv run scripts/update-task.py \
  --task-id '67f0a1b2c3d4e5f6g7h8i9j0' \
  --customfields '[{"customfieldId":"字段ID","value":[{"id":"","title":"document.pdf","metaString":"{\"fileToken\":\"eyJhbGci...\"}"}]}]'
```

---

## 重要说明

### 日期格式
- 必须使用 ISO 8601 格式（UTC 时间）
- 格式：`YYYY-MM-DDTHH:mm:ss.sssZ`
- 示例：`2026-03-15T00:00:00.000Z`
- 注意时区转换（用户输入默认东八区，API 要求零时区）

### 优先级映射
| 值 | 含义 |
|----|------|
| 0 | 低 |
| 1 | 中 |
| 2 | 高 |
| 3 | 紧急 |

### JSON 参数格式
- 使用单引号包裹 JSON 字符串
- JSON 内部使用双引号
- 示例：`'["id1","id2"]'`

### 并行执行特性
- 多个字段同时更新，显著提升性能
- 最多支持 10 个并发线程
- 每个字段独立更新，互不影响
- 实时显示每个字段的更新结果

---

## 相关文档

- [创建任务](create-task.md) - 创建任务完整指南
- [任务管理](task.md) - 任务管理功能概览
- [用户和成员管理](user.md) - 获取用户信息、查询企业成员
- [项目管理](project.md) - 查询项目列表和详情
- [最佳实践](BEST_PRACTICES.md) - 使用约束与最佳实践
- [错误处理](ERROR_HANDLING.md) - 常见错误及解决方案
