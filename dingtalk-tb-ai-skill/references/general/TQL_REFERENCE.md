# TQL 查询语言参考文档

## 概述

TQL（Teambition Query Language）是一种搜索 DSL（Domain Specific Language），用于 Teambition 搜索语句简化，目前已覆盖高级搜索场景。

## 使用接口

**通过 TQL 搜索企业下任务**

```
GET https://open.teambition.com/api/all-task/search?tql={{TQL}}
Authorization: {{AUTHORIZATION}}
x-tenant-id: {{X-TENANT-ID}}
```

官方文档：https://open.teambition.com/docs/apis/64264d3e912d20d3b5883b0e

## TQL 语法格式

**基本格式**：`筛选字段 + 操作符 + 值 + ORDER BY + 排序字段 + 升序/降序`

### 逻辑运算符

| 运算符 | 说明 |
| --- | --- |
| AND | 表达式之间「且」的关系 |
| OR | 表达式之间「或」的关系 |

### 操作符

| 操作符 | 说明 |
| --- | --- |
| ~ | 模糊匹配 |
| = | 等于 |
| != | 不等于 |
| > | 大于 |
| >= | 大于等于 |
| < | 小于 |
| <= | 小于等于 |
| IN | 选项之间取交集 |
| NOT IN | 选项之间取交集 |

### 筛选字段

| 筛选字段 | 操作符 | 说明 |
| --- | --- | --- |
| tagId | = ｜ != ｜IN ｜ NOT IN | 标签 |
| priority | = ｜ != ｜IN ｜ NOT IN | 优先级 |
| stageId | = ｜ != ｜IN ｜ NOT IN | 任务列表（自定义）|
| executorId | = ｜ != ｜IN ｜ NOT IN | 执行者 |
| creatorId | = ｜ != ｜IN ｜ NOT IN | 创建者 |
| involveMembers | = ｜ != ｜IN ｜ NOT IN | 参与者 |
| taskflowstatusId | = ｜ != ｜IN ｜ NOT IN | 任务状态 |
| scenarioId | = ｜ != ｜IN ｜ NOT IN | 任务类型 |
| tasklistId | = ｜ != ｜IN ｜ NOT IN | 任务分组 |
| accomplished | = ｜!= ｜ > ｜ >= ｜ < ｜ <= | 完成时间 |
| startDate | = ｜!= ｜ > ｜ >= ｜ < ｜ <= | 开始时间 |
| dueDate | = ｜!= ｜ > ｜ >= ｜ < ｜ <= | 截止时间 |
| created | = ｜!= ｜ > ｜ >= ｜ < ｜ <= | 创建时间 |
| updated | = ｜!= ｜ > ｜ >= ｜ < ｜ <= | 更新时间 |
| storyPoint | = ｜ != | SP |
| cf:id（number）| = ｜!= ｜ > ｜ >= ｜ < ｜ <= | 自定义字段（数字类型）|
| cf:id（text）| ~ ｜!~ | 自定义字段（文本类型）|
| cf:id（date）| = ｜!= ｜ > ｜ >= ｜ < ｜ <= | 自定义字段（日期类型）|
| cf:id（MultiSelect）| ~ ｜ !~ | 自定义字段（多选类型）|
| cf:id（radio）| = ｜ != ｜IN ｜ NOT IN | 自定义字段（单选类型）|
| text | ~ | 任务标题&备注&短ID |
| isDone | = ｜ != | 是否完成 |
| isArchived | = ｜ != | 是否归档 |
|title| ~ | 任务标题|

### 排序字段

| 排序字段 | 升序/降序 | 说明 |
| --- | --- | --- |
| startDate | ASC/DESC | 开始时间 |
| dueDate | ASC/DESC | 截止时间 |
| accomplished | ASC/DESC | 完成时间 |
| created | ASC/DESC | 创建时间 |
| updated | ASC/DESC | 更新时间 |
| priority | ASC/DESC | 优先级 |

## 用户查询函数

当需要查询与"我"（当前用户）相关的数据时，可以使用 `me()` 函数代替具体的用户 ID。

### me() 函数

**语法**：`{字段} = me()` 或 `{字段} != me()` 或 `{字段} IN me()` 或 `{字段} NOT IN me()`

**适用字段**：
- `executorId`：执行者
- `creatorId`：创建者
- `involveMembers`：参与者

**使用示例**：
```
# 查询我执行的任务
executorId = me()

# 查询我创建的任务
creatorId = me()

# 查询我参与的任务
involveMembers = me()

# 查询不是我执行的任务
executorId != me()

# 查询我执行或参与的任务
executorId = me() OR involveMembers = me()
```

**优势**：
- 无需手动填写用户 ID（24位十六进制字符串）
- 自动识别当前登录用户
- 代码更简洁易读
- 便于在不同用户间复用查询语句

## 时间查询模式

时间字段（created、dueDate、accomplished、startDate、updated 等）支持以下查询方式：

```
未填写：'$key$ = null'
今天以前：'$key$ <= endOf(d, -1d)'
今天：'$key$ <= endOf(d) AND $key$ >= startOf(d)'
昨天：'$key$ <= endOf(d, -1d) AND $key$ >= startOf(d, -1d)'
过去3天：'$key$ <= endOf(d, -1d) AND $key$ >= startOf(d, -3d)'
过去7天：'$key$ <= endOf(d, -1d) AND $key$ >= startOf(d, -7d)'
过去30天：'$key$ <= endOf(d, -1d) AND $key$ >= startOf(d, -30d)'
过去90天：'$key$ <= endOf(d, -1d) AND $key$ >= startOf(d, -90d)'
最近3天：'$key$ <= endOf(d) AND $key$ >= startOf(d, -2d)'
最近7天：'$key$ <= endOf(d) AND $key$ >= startOf(d, -6d)'
未来3天：'$key$ <= endOf(d, 3d) AND $key$ >= startOf(d, 1d)'
未来7天：'$key$ <= endOf(d, 7d) AND $key$ >= startOf(d, 1d)'
本周：'$key$ <= endOf(w) AND $key$ >= startOf(w)'
上周：'$key$ <= endOf(w, -1w) AND $key$ >= startOf(w, -1w)'
本月：'$key$ <= endOf(M) AND $key$ >= startOf(M)'
上月：'$key$ <= endOf(M, null, -1M) AND $key$ >= startOf(M, -1M)'
今年：'$key$ <= endOf(y) AND $key$ >= startOf(y)'
去年：'$key$ <= endOf(y, null, -1y) AND $key$ >= startOf(y, -1y)'
指定日期范围：'$key$ <= 2022-11-10T00:00:00+08:00 AND $key$ >= 2022-11-05T00:00:00+08:00'
```

**时间查询示例：**
- 今天截止的任务：`dueDate <= endOf(d) AND dueDate >= startOf(d)`
- 昨天完成的任务：`accomplished <= endOf(d, -1d) AND accomplished >= startOf(d, -1d)`
- 过去两天开始的任务：`startDate <= endOf(d) AND startDate >= startOf(d, -2d)`
- 本周创建的任务：`created <= endOf(w) AND created >= startOf(w)`

## 常用 TQL 示例

### 1. 按执行者查询

**查看今天以前截止的我执行的任务，按创建时间降序**
```
executorId = me() AND dueDate <= endOf(d, -1d) ORDER BY created DESC
```

**查看今天以前截止的指定用户执行的任务，按创建时间降序**
```
executorId = {USER_ID} AND dueDate <= endOf(d, -1d) ORDER BY created DESC
```

### 2. 复合条件查询

**查看过去七天创建的我执行且 SP 在 1-5 之间的任务，按更新时间降序**
```
storyPoint <= 5 AND storyPoint >= 1 AND executorId = me() AND created <= endOf(d, -1d) AND created >= startOf(d, -7d) ORDER BY updated DESC
```

### 3. 完成状态查询

**查看我作为执行者完成的且未归档的任务，按截止时间升序**
```
isDone = true AND executorId = me() AND isArchived = false ORDER BY dueDate ASC
```

### 4. 未填写/已填写字段查询

- 任务未指派：`executorId = null`
- 任务已指派：`executorId != null`
- 未设置截止时间：`dueDate = null`
- 已设置截止时间：`dueDate != null`

### 5. 可见性查询

**只返回我可见的任务**
```
myVisible = myVisible(true)
```

### 6. 文本搜索

**搜索标题或备注中包含关键词的任务**
```
text ~ "关键词"
```

## 常见查询场景

### 个人任务管理

| 场景 | TQL 表达式 |
| --- | --- |
| 我的待办任务 | `executorId = me() AND isDone = false` |
| 我的已完成任务 | `executorId = me() AND isDone = true` |
| 我的逾期任务 | `executorId = me() AND isDone = false AND dueDate < startOf(d)` |
| 我本周的任务 | `executorId = me() AND dueDate <= endOf(w) AND dueDate >= startOf(w)` |
| 我今天要完成的任务 | `executorId = me() AND dueDate <= endOf(d) AND dueDate >= startOf(d)` |
| 我创建的任务 | `creatorId = me()` |
| 我参与的任务 | `involveMembers = me()` |
| 我创建但未完成的任务 | `creatorId = me() AND isDone = false` |

### 团队任务管理

| 场景 | TQL 表达式 |
| --- | --- |
| 未指派的任务 | `executorId = null AND isDone = false` |
| 高优先级任务 | `priority = 0 AND isDone = false` |
| 本周创建的任务 | `created <= endOf(w) AND created >= startOf(w)` |
| 即将逾期的任务 | `isDone = false AND dueDate <= endOf(d, 3d) AND dueDate >= startOf(d)` |

## TQL 使用注意事项

1. **特殊字符转义**：TQL 中包含特殊字符时，请使用引号包裹并正确转义
2. **时间格式**：时间字段使用 ISO 8601 格式，如 `2022-11-10T00:00:00+08:00`
3. **ID 字段**：executorId、creatorId 等可以使用 `me()` 函数代表当前用户，或使用实际的用户 ID（24位十六进制字符串）
4. **自定义字段**：使用 `cf:id` 格式，其中 id 为自定义字段的 ID
5. **优先级值**：0=紧急，1=高，2=中，3=低
6. **布尔值**：isDone、isArchived 等使用 true/false
7. **me() 函数**：查询与"我"相关的数据时，推荐使用 `me()` 函数，更简洁且便于复用
