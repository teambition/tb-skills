附录：
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
