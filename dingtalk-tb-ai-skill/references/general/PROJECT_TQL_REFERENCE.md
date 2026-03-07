# 项目 TQL 查询语言参考文档

TQL（Teambition Query Language）是一种搜索 DSL（Domain Specific Language），用于 Teambition 搜索语句简化。本文档介绍企业下项目搜索的 TQL 使用说明。

## 使用接口

```
GET https://open.teambition.com/api/project/search?tql={{TQL}}
Authorization: {{AUTHORIZATION}}
x-tenant-id: {{X-TENANT-ID}}
```

**重要提示**：`isTemplate` 参数比较特殊，含义为是否是模板项目，建议 `isTemplate` 默认查询是 `false`，否则会查询到模板项目，以免影响到查询结果。

## TQL 语法格式

TQL 是一个字符串，由 filter + sort 组成：

```
筛选字段 + 操作符 + 值 + ORDER BY + 排序字段 + 升序/降序
```

### 逻辑运算符

| 运算符 | 说明 |
|--------|------|
| AND | 表达式之间「且」的关系 |
| OR | 表达式之间「或」的关系 |

### 操作符

| 操作符 | 说明 |
|--------|------|
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

| 字段 | 操作符 | 说明 |
|------|--------|------|
| creatorId | =, !=, IN, NOT IN | 创建者 ID（支持 `me()` 函数） |
| involveMembers | =, !=, IN, NOT IN | 项目成员 ID（支持 `me()` 函数） |
| created | =, !=, >, >=, <, <= | 创建时间 |
| updated | =, !=, >, >=, <, <= | 更新时间 |
| visibility | = | project: 私有项目<br>organization: 企业公开项目<br>org: 公开项目 |
| isArchived | = | 是否在回收站内 |
| isSuspended | = | 是否已归档 |
| isTemplate | = | 是否是模板项目（建议默认为 false） |
| text | ~ | 项目名称、项目简介 |
| nameText | = | 项目名称 |
| description | = | 项目简介 |
| cf:id（number） | =, !=, >, >=, <, <= | 自定义字段（数字类型） |
| cf:id（text） | =, != | 自定义字段（文本类型） |
| cf:id（date） | =, !=, >, >=, <, <= | 自定义字段（日期类型） |
| cf:id（MultiSelect） | =, !=, IN, NOT IN | 自定义字段（多选类型） |
| cf:id（radio） | =, !=, IN, NOT IN | 自定义字段（单选类型） |

### 排序字段

| 字段 | 升序/降序 | 说明 |
|------|-----------|------|
| created | ASC/DESC | 创建时间 |
| updated | ASC/DESC | 更新时间 |

## 时间函数

### 基础时间函数

- `startOf(d)` / `endOf(d)`：今天的开始/结束
- `startOf(w)` / `endOf(w)`：本周的开始/结束
- `startOf(M)` / `endOf(M)`：本月的开始/结束
- `startOf(y)` / `endOf(y)`：今年的开始/结束

### 时间偏移

支持使用偏移量来表示相对时间：

- `startOf(d, -7d)`：7 天前的开始
- `endOf(d, -1d)`：昨天的结束
- `startOf(w, -1w)`：上周的开始
- `endOf(M, null, -1M)`：上月的结束

### 时间查询示例

以下示例中的 `$key$` 可以替换为任意时间类型字段（如 `created`、`updated`）：

| 场景 | TQL 表达式 |
|------|-----------|
| 未填写 | `$key$ = null` |
| 今天以前 | `$key$ <= endOf(d, -1d)` |
| 今天 | `$key$ <= endOf(d) AND $key$ >= startOf(d)` |
| 昨天 | `$key$ <= endOf(d, -1d) AND $key$ >= startOf(d, -1d)` |
| 过去3天 | `$key$ <= endOf(d, -1d) AND $key$ >= startOf(d, -3d)` |
| 过去7天 | `$key$ <= endOf(d, -1d) AND $key$ >= startOf(d, -7d)` |
| 过去30天 | `$key$ <= endOf(d, -1d) AND $key$ >= startOf(d, -30d)` |
| 过去90天 | `$key$ <= endOf(d, -1d) AND $key$ >= startOf(d, -90d)` |
| 最近3天 | `$key$ <= endOf(d) AND $key$ >= startOf(d, -2d)` |
| 最近7天 | `$key$ <= endOf(d) AND $key$ >= startOf(d, -6d)` |
| 未来3天 | `$key$ <= endOf(d, 3d) AND $key$ >= startOf(d, 1d)` |
| 未来7天 | `$key$ <= endOf(d, 7d) AND $key$ >= startOf(d, 1d)` |
| 本周 | `$key$ <= endOf(w) AND $key$ >= startOf(w)` |
| 上周 | `$key$ <= endOf(w, -1w) AND $key$ >= startOf(w, -1w)` |
| 本月 | `$key$ <= endOf(M) AND $key$ >= startOf(M)` |
| 上月 | `$key$ <= endOf(M, null, -1M) AND $key$ >= startOf(M, -1M)` |
| 今年 | `$key$ <= endOf(y) AND $key$ >= startOf(y)` |
| 去年 | `$key$ <= endOf(y, null, -1y) AND $key$ >= startOf(y, -1y)` |
| 指定日期范围 | `$key$ <= 2022-11-10T00:00:00+08:00 AND $key$ >= 2022-11-05T00:00:00+08:00` |

## 常见查询场景

### 基础查询

```tql
# 查询企业内所有项目
""

# 查询包含"测试"的项目
nameText ~ '测试'

# 查询在回收站的项目
isArchived = true

# 查询已归档的项目
isSuspended = true

# 查询模板项目
isTemplate = true
```

### 用户相关查询

```tql
# 我创建的项目
creatorId = me()

# 我参与的项目
involveMembers = me()

# 指定用户创建的项目
creatorId = {USER_ID}
```

### 时间相关查询

```tql
# 今天更新的项目
updated <= endOf(d) AND updated >= startOf(d)

# 昨天创建的项目
created <= endOf(d, -1d) AND created >= startOf(d, -1d)

# 过去7天创建的项目
created <= endOf(d, -1d) AND created >= startOf(d, -7d)

# 本周创建的项目
created <= endOf(w) AND created >= startOf(w)

# 本月更新的项目
updated <= endOf(M) AND updated >= startOf(M)
```

### 组合查询

```tql
# 过去7天创建的、我创建的、未归档、不在回收站、非模板项目，按更新时间降序
isTemplate = false AND isArchived = false AND isSuspended = false AND creatorId = me() AND created <= endOf(d, -1d) AND created >= startOf(d, -7d) ORDER BY updated DESC

# 包含"开发"且未归档的项目
nameText ~ '开发' AND isSuspended = false

# 我参与的且今天有更新的项目
involveMembers = me() AND updated <= endOf(d) AND updated >= startOf(d)
```

### 自定义字段查询

```tql
# 查询"项目目标"自定义字段包含"上线"的项目
# 假设 609e13e0cea6e8205508f350 为"项目目标"自定义字段 ID
(cf:609e13e0cea6e8205508f350 ~ '上线') AND isArchived = false AND isTemplate = false
```

## 最佳实践

### 1. 默认排除模板项目

建议在查询时默认添加 `isTemplate = false` 条件，避免查询到模板项目：

```tql
# 推荐
isTemplate = false AND nameText ~ '测试'

# 不推荐（可能包含模板项目）
nameText ~ '测试'
```

### 2. 使用 me() 函数

查询当前用户相关的项目时，使用 `me()` 函数而不是具体的用户 ID：

```tql
# 推荐
creatorId = me()

# 不推荐
creatorId = 5f9a1b2c3d4e5f6g7h8i9j0k
```

### 3. 合理使用排序

对于时间相关的查询，建议添加排序以获得更好的结果：

```tql
# 按更新时间降序（最新的在前）
created >= startOf(w) ORDER BY updated DESC

# 按创建时间升序（最早的在前）
created >= startOf(M) ORDER BY created ASC
```

### 4. 组合条件的括号使用

对于复杂的组合条件，建议使用括号明确优先级：

```tql
# 推荐
(nameText ~ '测试' OR nameText ~ '开发') AND isArchived = false

# 不推荐（可能产生歧义）
nameText ~ '测试' OR nameText ~ '开发' AND isArchived = false
```

## 参考资料

- [Teambition 开放平台文档](https://open.teambition.com/docs)
- [任务 TQL 参考文档](./TQL_REFERENCE.md)
