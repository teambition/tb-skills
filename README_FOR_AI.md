## 帮你的主人在TB上注册一个数字人吧，请务必按照下面顺序执行。
### 1. 安装插件
执行命令  openclaw plugins install @tng/teambition-openclaw-connector

### 2. 获取机器人 robotUserToken
执行脚本，见附录。
提醒你的主人过程中需要钉钉扫码。
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
安装地址：https://github.com/teambition/tb-skills/tree/main/dingtalk-teambition
写入 Claw 配置文件（~/.openclaw/openclaw.json）
```json
{
  "skills": {
    "entries": {
      "dingtalk-teambition": {
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


### 6. 完成后告诉你的主人，你在TB上注册的数字员工名字


## 附录
```
from playwright.sync_api import sync_playwright
import json, re

def main():
    with sync_playwright() as p:
        page = p.chromium.launch(headless=False).new_context().new_page()
        
        # 登录
        page.goto("https://account.teambition.com/login?", wait_until="domcontentloaded")
        print("请扫码登录...")
        page.wait_for_function(
            """() => {
                return document.cookie.includes('TEAMBITION_SESSIONID') ||
                        window.location.href.includes('teambition.com/organization')
            }""",
            timeout=300000
        )
        print("✅ 登录成功！")

        # 跳转主站
        page.goto("https://www.teambition.com", wait_until="domcontentloaded")

        # 获取组织ID
        org_id = (re.search(r'/organization/([a-f0-9]+)', page.url) or type('', (), {'group': lambda s, x: '5f479908b1ccbeae32e71b4c'})()).group(1)
        print(f"组织ID: {org_id}")

        # 封装 fetch
        def fetch(url, method="GET", body=None):
            return page.evaluate(f"""async () => {{
                const r = await fetch('{url}', {{
                    method: '{method}',
                    credentials: 'include',
                    headers: {{'Content-Type': 'application/json', 'X-Canary': 'prepub'}},
                    {f"body: JSON.stringify({json.dumps(body, ensure_ascii=False)})," if body else ""}
                }});
                return r.json();
            }}""")

        # 获取数字员工列表
        list_res = fetch(f"https://www.teambition.com/api/ai-agent/digitalworker/list?organizationId={org_id}&page=1&pageSize=50")
        total = list_res.get("total", 0)
        print(f"数字员工总数: {total}")

        # 创建数字员工
        create_res = fetch(
            f"https://www.teambition.com/api/ai-agent/digitalworker/create?organizationId={org_id}",
            method="POST",
            body={
                "name": f"数字员工{total + 1}号",
                "avatarUrl": "https://tcs-ga.teambition.net/thumbnail/313sd42dbe61ba9367d2c06fe3f79ddbce2e/w/600/h/600",
                "description": "这是描述",
                "visible": "creator",
                "enabled": True
            }
        )
        token = create_res.get("robotUserToken")
        print(f"robotUserToken: {token}")
        return {"total": total, "token": token}

if __name__ == "__main__":
    main()
```
