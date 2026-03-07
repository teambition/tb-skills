# 钉钉 Teambition Skill

OpenClaw 技能，用于操作钉钉 Teambition 项目和任务。通过 User Token 认证，使用 TQL（查询语言）灵活查询和管理 Teambition 项目、任务、成员等。

## 功能特性

- ✅ 用户和成员管理（获取用户信息、查询企业成员）
- ✅ 项目管理（查询项目列表和详情）
- ✅ 任务管理（创建、更新、查询、归档任务）
- ✅ 任务评论（创建评论、@ 成员、添加附件）
- ✅ 任务动态（查询任务操作历史）
- ✅ 任务进展（获取和创建任务进展）
- ✅ 文件管理（上传文件到任务）
- ✅ 优先级管理（查询和更新任务优先级）
- ✅ TQL 查询语言（灵活的任务和项目查询）

## 前置要求

### 1. Python 环境

本技能使用 Python 脚本，需要安装 `uv` 包管理器。

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

验证安装：
```bash
uv --version
```

### 2. 获取 Teambition User Token

1. 访问 Teambition User MCP 页面：
   https://open.teambition.com/user-mcp
2. 点击"创建 Token"按钮
3. 配置 Token：
   - Token 名称：`skill-mcp`
   - 有效期：1 年
   - 选择使用企业
4. 点击确认后，点击"查看详情"获取 Token ID

### 3. 配置环境变量

```bash
export TB_USER_TOKEN="your_user_token_here"
```

或者创建 `user-token.json` 文件：
```json
{
  "userToken": "your_user_token_here"
}
```

## 快速开始

### 安装技能

```bash
# 方式 1：使用 clawhub（推荐）
clawhub install dingtalk-tb-ai-skill

# 方式 2：直接对 OpenClaw 说
"安装 dingtalk-tb-ai-skill 这个 skill"
```

### 安装依赖

```bash
cd dingtalk-tb-ai-skill
uv sync
```

### 验证配置

```bash
# 获取当前用户信息
uv run scripts/get-current-user.py
```

成功时会返回包含用户信息的 JSON，例如：
```json
{
  "id": "xxx",
  "name": "张三",
  "email": "zhangsan@example.com"
}
```

### 创建第一个任务

跟你的 Claw 对话：
- "在项目 xxx 中创建一个任务"
- "创建一个任务，标题是'测试任务'，执行者是我"

## 使用示例

### 用户和成员

```bash
# 获取我的用户信息
uv run scripts/get-current-user.py

# 查询成员
uv run scripts/query-members.py --keyword "张三"
```

或者直接对 Claw 说：
- "获取我的用户信息"
- "查询成员张三"

### 项目管理

```bash
# 查询我创建的项目
uv run scripts/query-projects.py --tql "creatorId = me()"

# 查询项目详情
uv run scripts/query-projects-detail.py --project-id "xxx"
```

或者直接对 Claw 说：
- "查询我创建的项目"
- "查看项目 xxx 的详情"

### 任务管理

```bash
# 创建任务
uv run scripts/create-task.py --project-id "xxx" --content "任务标题"

# 查询我的待办任务
uv run scripts/query-tasks.py --tql "executorId = me() AND isDone = false"

# 更新任务状态
uv run scripts/update-task.py --task-id "xxx" --status "进行中"
```

或者直接对 Claw 说：
- "创建一个任务"
- "查询我的待办任务"
- "将任务 xxx 标记为进行中"

## 故障排查

### Token 认证失败

1. 检查 `TB_USER_TOKEN` 环境变量是否正确设置
2. 确认 Token 是否过期（访问 https://open.teambition.com/user-mcp 查看）
3. 确认 Token 是否有正确的企业权限

### 脚本执行失败

1. 检查 `uv` 是否正确安装：`uv --version`
2. 确认依赖已安装：`uv sync`
3. 检查 Python 版本（需要 Python 3.8+）

### TQL 查询错误

1. 参考 [TQL 查询语言文档](references/general/TQL_REFERENCE.md)
2. 检查查询语法是否正确
3. 确认字段名称是否正确（区分大小写）

## 详细文档

### 功能文档
- [用户和成员管理](references/user.md) - 获取用户信息、查询企业成员
- [项目管理](references/project.md) - 查询项目列表和详情
- [任务管理](references/task.md) - 查询任务列表和详情
- [创建任务](references/create-task.md) - 创建任务的详细说明
- [更新任务](references/update-task.md) - 更新任务的详细说明
- [任务进展管理](references/task-trace.md) - 获取和创建任务进展
- [文件管理](references/file-upload.md) - 上传文件到 Teambition
- [优先级管理](references/priority.md) - 查询和更新任务优先级

### 参考文档
- [TQL 查询语言](references/general/TQL_REFERENCE.md) - 任务查询语言完整参考
- [项目 TQL 参考](references/general/PROJECT_TQL_REFERENCE.md) - 项目查询语言完整参考
- [最佳实践](references/general/BEST_PRACTICES.md) - 使用约束与最佳实践
- [错误处理](references/general/ERROR_HANDLING.md) - 常见错误及解决方案

## 相关链接

- 📊 [Teambition 官网](https://www.teambition.com)
- 🔌 [Teambition 开放平台](https://open.teambition.com)
- 📦 [ClawHub 技能页面](https://clawhub.ai)
- 🐛 [问题反馈 (GitHub Issues)](https://github.com/teambition-taskcenter/tb-skills/issues)
- 📖 [源代码仓库](https://github.com/teambition-taskcenter/tb-skills)

## 技术支持

如有问题，请通过 GitHub Issues 反馈，或联系 Teambition 技术支持团队。

## ⚠️ 安全须知

**使用前请注意：**

1. **妥善保管 Token** - User Token 具有完整的账号权限，请勿泄露
2. **脚本审查建议** - `scripts/` 目录包含 Python 辅助脚本，建议先审查再运行
3. **测试环境优先** - 首次使用建议在测试项目中验证，确认无误后再操作生产数据
4. **日期时区转换** - 处理日期字段时注意时区转换（用户输入默认为东八区 UTC+8，API 要求零时区 UTC）

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。
