# 创建任务

本文档介绍如何使用 Teambition API 创建任务，包括核心字段说明、参数组装方案、字段映射和转换指引。

## 📚 目录

- [快速开始](#快速开始)
- [核心字段说明](#核心字段说明)
- [字段映射与转换](#字段映射与转换)
- [使用示例](#使用示例)
- [辅助脚本](#辅助脚本)
- [常见问题](#常见问题)

---

## 快速开始

### 最简单的创建

```bash
uv run scripts/create-task.py \
  --project-id '69a03cd9cd778ff7d8974858' \
  --content '完成需求文档'
```

### 完整参数创建

```bash
uv run scripts/create-task.py \
  --project-id '67ec9b8c3c6130ac88605c3e' \
  --content '实现用户管理功能' \
  --executor-id '696f2c084a459842b42b035b' \
  --due-date '2026-03-15T00:00:00.000Z' \
  --priority 1 \
  --note '需要实现增删改查功能'
```

---

## 核心字段说明

### 必填字段

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `projectId` | string | 项目 ID | `'69a03cd9cd778ff7d8974858'` |
| `content` | string | 任务标题 | `'完成需求文档'` |

### 可选字段

| 字段 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `executorId` | string | 执行人 ID | 无 |
| `involveMembers` | array | 参与者 ID 列表 | `[]` |
| `taskflowstatusId` | string | 任务状态 ID | 项目默认状态 |
| `startDate` | string | 开始日期（ISO 8601） | 无 |
| `dueDate` | string | 截止日期（ISO 8601） | 无 |
| `note` | string | 任务备注 | 无 |
| `priority` | integer | 优先级（0-3） | 无 |
| `parentTaskId` | string | 父任务 ID | 无 |
| `progress` | integer | 进度（0-100） | 0 |
| `visible` | string | 可见性 | `'members'` |
| `storyPoint` | string | 故事点 | 无 |
| `scenariofieldconfigId` | string | 任务类型 ID | 项目默认类型 |
| `customfields` | array | 自定义字段 | `[]` |

---

## 字段映射与转换

### 1. 项目标识（projectId）

**获取方式**：

```bash
# 方式 1: 查询项目列表
uv run scripts/query-projects.py --tql "involveMembers = me()"

# 方式 2: 通过项目名称搜索
uv run scripts/query-projects.py --tql "nameText ~ '项目名称'"
```

**使用示例**：
```bash
--project-id '67ec9b8c3c6130ac88605c3e'
```

---

### 2. 执行人（executorId）

**获取方式**：

```bash
# 查询成员
uv run scripts/query-members.py --keyword '张三'

# 获取当前用户
uv run scripts/get-current-user.py
```

**使用示例**：
```bash
--executor-id '696f2c084a459842b42b035b'
```

---

### 3. 参与者列表（involveMembers）

**数据类型**：JSON 数组

**格式**：
```json
["用户ID1", "用户ID2", "用户ID3"]
```

**获取方式**：
```bash
# 查询多个成员
uv run scripts/query-members.py --keyword '张三'
uv run scripts/query-members.py --keyword '李四'
```

**使用示例**：
```bash
--involve-members '["696f2c084a459842b42b035b", "696f2c084a459842b42b035c"]'
```

---

### 4. 任务类型（scenariofieldconfigId）

**获取方式**：

```bash
# 获取项目的所有任务类型
uv run scripts/get-scenario-types.py '67ec9b8c3c6130ac88605c3e'

# 获取默认任务类型
uv run scripts/get-scenario-types.py '67ec9b8c3c6130ac88605c3e' --default

# 根据名称搜索任务类型（支持模糊匹配）
uv run scripts/get-scenario-types.py '67ec9b8c3c6130ac88605c3e' --q '需求'
uv run scripts/get-scenario-types.py '67ec9b8c3c6130ac88605c3e' --q '缺陷'
```

**返回示例**：
```json
[
  {
    "id": "67ec9b8c3c6130ac88605c47",
    "name": "需求",
    "icon": "icon-requirement",
    "taskflowId": "67ec9b8c3c6130ac88605c40",
    "scenariofields": [
      {
        "customfieldId": "67ec9b8c3c6130ac88605c49",
        "fieldType": "select",
        "required": true
      }
    ]
  },
  {
    "id": "67ec9b8c3c6130ac88605c48",
    "name": "缺陷",
    "icon": "icon-bug",
    "taskflowId": "67ec9b8c3c6130ac88605c41",
    "scenariofields": []
  }
]
```

**重要字段说明**：
- `taskflowId`：工作流 ID，可以用来查询这个任务类型支持的状态列表
- `scenariofields`：这个任务类型绑定的自定义字段配置，包含字段 ID、类型和是否必填等信息

**使用示例**：
```bash
--scenariofieldconfig-id '67ec9b8c3c6130ac88605c47'
```

---

### 5. 任务状态（taskflowstatusId）

**获取方式**：

通过工作流 ID 获取状态。当你通过 `get-scenario-types.py` 获取任务类型后，可以使用返回的 `taskflowId` 查询该类型支持的状态：

```bash
# 获取指定工作流的所有状态
uv run scripts/get-taskflow-statuses.py '69a249b3ae5a104f017f6f0c' \
  --taskflow-id '69a249b39500e432f6399a13'

# 只获取可用于创建任务的状态 (kind=start)
uv run scripts/get-taskflow-statuses.py '67ec9b8c3c6130ac88605c3e' \
  --taskflow-id '67ec9b8c3c6130ac88605c40' \
  --only-start

# 根据名称搜索状态
uv run scripts/get-taskflow-statuses.py '67ec9b8c3c6130ac88605c3e' --q '未开始'
```

**返回示例**：
```json
[
  {
    "id": "67ec9b8c3c6130ac88605c44",
    "name": "未开始",
    "kind": "start",
    "taskflowId": "67ec9b8c3c6130ac88605c40"
  },
  {
    "id": "67ec9b8c3c6130ac88605c45",
    "name": "进行中",
    "kind": "process",
    "taskflowId": "67ec9b8c3c6130ac88605c40"
  },
  {
    "id": "67ec9b8c3c6130ac88605c46",
    "name": "已完成",
    "kind": "end",
    "taskflowId": "67ec9b8c3c6130ac88605c40"
  }
]
```

**重要说明**：
- 创建任务时，只能使用 `kind=start` 的状态作为初始状态
- 如果不指定 `taskflowstatusId`，系统会使用项目的默认状态
- 使用 `--only-start` 参数可以直接筛选出可用于创建任务的状态

**使用示例**：
```bash
--taskflowstatus-id '67ec9b8c3c6130ac88605c44'
```

---

### 6. 日期字段（startDate / dueDate）

**格式要求**：ISO 8601 格式（UTC 时间）

**格式示例**：
- `2026-03-15T00:00:00.000Z`
- `2026-12-31T23:59:59.999Z`

**使用示例**：
```bash
--start-date '2026-03-01T00:00:00.000Z' \
--due-date '2026-03-15T23:59:59.999Z'
```

**注意**：日期转换需要考虑时区问题，详见 SKILL.md 中的时区转换规则

---

### 7. 优先级（priority）

**获取方式**：

通过企业优先级接口获取可用的优先级列表：

```bash
# 调用 API 获取企业优先级
uv run scripts/call-user-api.py GET "v3/project/priority/list"
```

**返回示例**：
```json
{
  "result": [
    {"name": "低", "priority": 0},
    {"name": "中", "priority": 1},
    ...
  ],
  "defaultOptionId": "67ec9b8c3c6130ac88605c52"
}
```

**取值范围**：0-3（数值越大，优先级越高）

**映射关系**：
| 值 | 含义 |
|----|------|
| 0 | 低 |
| 1 | 中 |
| 2 | 高 |
| 3 | 紧急 |

**使用示例**：
```bash
--priority 2  # 高优先级
```

---

### 8. 进度（progress）

**取值范围**：0-100（整数）

**含义**：任务完成百分比

**使用示例**：
```bash
--progress 50  # 完成 50%
```

---

### 9. 可见性（visible）

**可选值**：
| 值 | 含义 |
|----|------|
| `involves` | 仅参与者可见 |
| `members` | 项目成员可见 |

**使用示例**：
```bash
--visible 'involves'  # 仅参与者可见
```

---

### 10. 自定义字段（customfields）

**数据类型**：JSON 数组

**格式结构**：
```json
[
  {
    "cfId": "自定义字段ID",
    "value": [
      {
        "id": "字段值ID",
        "title": "字段值内容"
      }
    ]
  }
]
```

#### 获取自定义字段配置

```bash
# 获取项目的所有自定义字段
uv run scripts/get-custom-fields.py '67ec9b8c3c6130ac88605c3e'

# 获取特定任务类型的自定义字段
uv run scripts/get-custom-fields.py '67ec9b8c3c6130ac88605c3e' \
  --sfc-id '67ec9b8c3c6130ac88605c47'
```

**返回示例**：
```json
[
  {
    "id": "67ec9b8c3c6130ac88605c49",
    "name": "需求类型",
    "type": "select",
    "choices": [
      {
        "id": "67ec9b8c3c6130ac88605c4a",
        "value": "功能需求"
      },
      {
        "id": "67ec9b8c3c6130ac88605c4b",
        "value": "性能优化"
      }
    ]
  }
]
```

#### 不同类型字段的填写方式

**1. 单选字段（select）**

```json
[
  {
    "cfId": "67ec9b8c3c6130ac88605c49",
    "value": [
      {
        "id": "67ec9b8c3c6130ac88605c4a",
        "title": "功能需求"
      }
    ]
  }
]
```

**2. 多选字段（multiselect）**

```json
[
  {
    "cfId": "67ec9b8c3c6130ac88605c4c",
    "value": [
      {
        "id": "67ec9b8c3c6130ac88605c4d",
        "title": "前端"
      },
      {
        "id": "67ec9b8c3c6130ac88605c4e",
        "title": "后端"
      }
    ]
  }
]
```

**3. 文本字段（text）**

```json
[
  {
    "cfId": "67ec9b8c3c6130ac88605c4f",
    "value": [
      {
        "id": "",
        "title": "这是文本内容"
      }
    ]
  }
]
```

**4. 数字字段（number）**

```json
[
  {
    "cfId": "67ec9b8c3c6130ac88605c50",
    "value": [
      {
        "id": "",
        "title": "100"
      }
    ]
  }
]
```

**5. 日期字段（date）**

```json
[
  {
    "cfId": "67ec9b8c3c6130ac88605c51",
    "value": [
      {
        "id": "",
        "title": "2026-03-15T00:00:00.000Z"
      }
    ]
  }
]
```

**6. 成员字段（member）**

```json
[
  {
    "cfId": "67ec9b8c3c6130ac88605c52",
    "value": [
      {
        "id": "696f2c084a459842b42b035b",
        "title": "696f2c084a459842b42b035b"
      }
    ]
  }
]
```

**注意**：成员字段的 `id` 和 `title` 都填写用户 ID，系统会自动翻译成用户名称。

**7. 文件字段（file）**

```json
[
  {
    "cfId": "67ec9b8c3c6130ac88605c53",
    "value": [
      {
        "id": "",
        "title": "文件名.pdf",
        "metaString": "{\"fileToken\":\"file_token_here\"}"
      }
    ]
  }
]
```

**注意**：文件字段需要先调用文件上传接口获取 `fileToken`。

#### 使用示例

**单个自定义字段**：
```bash
--customfields '[{"cfId":"67ec9b8c3c6130ac88605c49","value":[{"id":"67ec9b8c3c6130ac88605c4a","title":"功能需求"}]}]'
```

**多个自定义字段**：
```bash
--customfields '[
  {
    "cfId": "67ec9b8c3c6130ac88605c49",
    "value": [{"id": "67ec9b8c3c6130ac88605c4a", "title": "功能需求"}]
  },
  {
    "cfId": "67ec9b8c3c6130ac88605c4f",
    "value": [{"id": "", "title": "这是备注信息"}]
  }
]'
```

---

## 使用示例

### 示例 1: 最简单创建

只提供必填字段：

```bash
uv run scripts/create-task.py \
  --project-id '67ec9b8c3c6130ac88605c3e' \
  --content '完成需求文档'
```

### 示例 2: 指定执行人和截止日期

```bash
uv run scripts/create-task.py \
  --project-id '67ec9b8c3c6130ac88605c3e' \
  --content '修复登录bug' \
  --executor-id '696f2c084a459842b42b035b' \
  --due-date '2026-03-20T23:59:59.999Z' \
  --priority 0
```

### 示例 3: 创建子任务

```bash
uv run scripts/create-task.py \
  --project-id '67ec9b8c3c6130ac88605c3e' \
  --content '编写单元测试' \
  --parent-task-id '67ec9b8c3c6130ac88605c43' \
  --executor-id '696f2c084a459842b42b035b'
```

### 示例 4: 带参与者和自定义字段

```bash
uv run scripts/create-task.py \
  --project-id '67ec9b8c3c6130ac88605c3e' \
  --content '实现用户管理功能' \
  --executor-id '696f2c084a459842b42b035b' \
  --involve-members '["696f2c084a459842b42b035c", "696f2c084a459842b42b035d"]' \
  --scenariofieldconfig-id '67ec9b8c3c6130ac88605c47' \
  --due-date '2026-03-15T23:59:59.999Z' \
  --priority 1 \
  --note '需要实现增删改查功能' \
  --customfields '[{"cfId":"67ec9b8c3c6130ac88605c49","value":[{"id":"67ec9b8c3c6130ac88605c4a","title":"功能需求"}]}]'
```

### 示例 5: 完整参数创建

```bash
uv run scripts/create-task.py \
  --project-id '67ec9b8c3c6130ac88605c3e' \
  --content '实现用户权限管理模块' \
  --executor-id '696f2c084a459842b42b035b' \
  --involve-members '["696f2c084a459842b42b035c"]' \
  --taskflowstatus-id '67ec9b8c3c6130ac88605c44' \
  --start-date '2026-03-01T00:00:00.000Z' \
  --due-date '2026-03-31T23:59:59.999Z' \
  --note '需要实现角色管理、权限分配、权限验证等功能' \
  --priority 1 \
  --progress 0 \
  --visible 'members' \
  --story-point '8' \
  --scenariofieldconfig-id '67ec9b8c3c6130ac88605c47'
```

---

## 辅助脚本

### 1. 获取任务类型

**脚本**: `scripts/get-scenario-types.py`

**功能**: 获取项目的任务类型列表及配置

**使用示例**:
```bash
# 获取所有任务类型
uv run scripts/get-scenario-types.py '67ec9b8c3c6130ac88605c3e'

# 获取默认任务类型
uv run scripts/get-scenario-types.py '67ec9b8c3c6130ac88605c3e' --default

# 根据名称搜索任务类型（支持模糊匹配）
uv run scripts/get-scenario-types.py '67ec9b8c3c6130ac88605c3e' --q '需求'
uv run scripts/get-scenario-types.py '67ec9b8c3c6130ac88605c3e' --q '缺陷'

# 获取指定 ID 的任务类型
uv run scripts/get-scenario-types.py '67ec9b8c3c6130ac88605c3e' --scenario-id '67ec9b8c3c6130ac88605c47'
```

### 2. 获取工作流状态

**脚本**: `scripts/get-taskflow-statuses.py`

**功能**: 获取项目的工作流状态列表

**使用示例**:
```bash
# 获取项目所有工作流状态
uv run scripts/get-taskflow-statuses.py '67ec9b8c3c6130ac88605c3e'

# 获取指定工作流的状态
uv run scripts/get-taskflow-statuses.py '67ec9b8c3c6130ac88605c3e' \
  --taskflow-id '67ec9b8c3c6130ac88605c40'

# 只获取可用于创建任务的状态 (kind=start)
uv run scripts/get-taskflow-statuses.py '67ec9b8c3c6130ac88605c3e' --only-start

# 根据名称搜索状态
uv run scripts/get-taskflow-statuses.py '67ec9b8c3c6130ac88605c3e' --q '未开始'
```

### 3. 获取自定义字段

**脚本**: `scripts/get-custom-fields.py`

**功能**: 批量获取项目的自定义字段配置

**使用示例**:
```bash
# 获取所有自定义字段
uv run scripts/get-custom-fields.py '67ec9b8c3c6130ac88605c3e'

# 批量获取指定字段
uv run scripts/get-custom-fields.py '67ec9b8c3c6130ac88605c3e' \
  --cf-ids '67ec9b8c3c6130ac88605c3f,67ec9b8c3c6130ac88605c40'

# 获取特定任务类型的字段
uv run scripts/get-custom-fields.py '67ec9b8c3c6130ac88605c3e' \
  --sfc-id '67ec9b8c3c6130ac88605c47'
```

---

## 常见问题

### 1. 如何获取项目 ID？

**方法 1：查询我参与的项目**
```bash
uv run scripts/query-projects.py --tql "involveMembers = me()"
```

**方法 2：通过项目名称搜索**
```bash
uv run scripts/query-projects.py --tql "nameText ~ '项目名称'"
```

### 2. 如何获取用户 ID？

**查询成员**
```bash
uv run scripts/query-members.py --keyword '张三'
```

**获取当前用户**
```bash
uv run scripts/get-current-user.py
```

### 3. 日期格式如何转换？

日期必须使用 ISO 8601 格式（UTC 时间），格式示例：`2026-03-15T00:00:00.000Z`

**注意**：日期转换需要考虑时区问题（用户输入默认为东八区，API 要求零时区），详见 SKILL.md 中的时区转换规则

### 4. 如何查看项目的任务状态？

通过工作流状态查询接口获取：

```bash
# 获取项目所有工作流状态
uv run scripts/get-taskflow-statuses.py '项目ID'

# 只获取可用于创建任务的状态
uv run scripts/get-taskflow-statuses.py '项目ID' --only-start
```

### 5. 自定义字段如何填写？

**步骤 1：获取自定义字段配置**
```bash
uv run scripts/get-custom-fields.py '项目ID'
```

**步骤 2：根据字段类型构造 JSON**

参考 [字段映射与转换](#字段映射与转换) 章节中的自定义字段部分。

### 6. JSON 参数如何传递？

对于数组类型的参数（如 `involveMembers`、`customfields`），需要传递 JSON 字符串：

```bash
# 参与者列表
--involve-members '["用户ID1", "用户ID2"]'

# 自定义字段
--customfields '[{"cfId":"字段ID","value":[{"id":"值ID","title":"值内容"}]}]'
```

**注意**：JSON 字符串需要用单引号包裹，内部使用双引号。

### 7. 提示"无法获取 User Token"怎么办？

请确保已配置 User Token：

**方式 1：环境变量**
```bash
export TB_USER_TOKEN="your_token_here"
```

**方式 2：配置文件**
创建 `user-token.json`：
```json
{
  "userToken": "your_token_here"
}
```

### 8. 如何创建子任务？

使用 `--parent-task-id` 参数指定父任务 ID：

```bash
uv run scripts/create-task.py \
  --project-id '项目ID' \
  --content '子任务标题' \
  --parent-task-id '父任务ID'
```

### 9. 优先级数值对应关系是什么？

数值越大，优先级越高：

| 值 | 含义 |
|----|------|
| 0 | 低 |
| 1 | 中 |
| 2 | 高 |
| 3 | 紧急 |

### 10. 可见性参数有哪些选项？

| 值 | 含义 |
|----|------|
| `involves` | 仅参与者可见 |
| `members` | 项目成员可见（默认） |

---

## 相关文档

- [用户和成员管理](user.md) - 获取用户信息、查询企业成员
- [项目管理](project.md) - 查询项目列表和详情
- [任务管理](task.md) - 查询任务列表和详情
- [最佳实践](BEST_PRACTICES.md) - 使用约束与最佳实践
- [错误处理](ERROR_HANDLING.md) - 常见错误及解决方案
