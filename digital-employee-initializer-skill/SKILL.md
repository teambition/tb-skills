帮我安装下插件，按照下面顺序执行。
### 1. 安装插件
执行命令  openclaw plugins install @tng/teambition-openclaw-connector

### 2. 获取机器人 robotUserToken
执行脚本，地址：https://github.com/teambition/tb-skills/tree/main/digital-employee-initializer-skill/scripts/init.py。
该脚本需要安装必要依赖
```
pip install playwright
python -m playwright install chromium
```

### 3. 配置 Connector
编辑 ~/.openclaw/openclaw.json：
```json
{
  "channels": {
    "teambition-openclaw-connector": {
      "token": "YOUR_BOT_TOKEN"
    }
  }
}
```

### 4. 安装teambition skill
安装地址：https://github.com/teambition/tb-skills/tree/main/dingtalk-tb-ai-skill
写入 Claw 配置文件（~/.openclaw/openclaw.json）
```json
{
  "skills": {
    "entries": {
      "dingtalk-tb-ai-skill": {
        "enabled": true,
        "env": { "TB_USER_TOKEN": "YOUR_BOT_TOKEN" }
      }
    }
  }
}
```

### 5. 启动并验证
重启 Gateway：
```
openclaw gateway restart
openclaw plugins list   # 验证插件已加载
```