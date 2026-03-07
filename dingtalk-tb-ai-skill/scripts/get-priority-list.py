#!/usr/bin/env python3
"""
获取企业优先级列表脚本
调用 /v3/project/priority/list 接口获取企业可用的优先级配置
"""

import requests
import json
import sys
import os

# ================= 配置信息 =================
USER_TOKEN = os.environ.get("TB_USER_TOKEN")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = "user-token.json"
CONFIG_PATHS = [
    os.path.join(os.getcwd(), CONFIG_FILE),
    os.path.join(SCRIPT_DIR, CONFIG_FILE),
    os.path.join(SCRIPT_DIR, "..", CONFIG_FILE),
    CONFIG_FILE
]
# ===========================================

def load_user_token():
    """加载 User Token"""
    if USER_TOKEN:
        return USER_TOKEN
    
    for config_path in CONFIG_PATHS:
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    token = config.get('userToken')
                    if token:
                        return token
            except Exception as e:
                print(f"❌ 读取配置文件 {config_path} 失败: {e}")
    
    return None

def get_priority_list(organization_id):
    """
    获取企业可用的优先级列表
    
    Args:
        organization_id: 企业/组织 ID
    
    Returns:
        list: 优先级列表，失败返回 None
    """
    try:
        token = load_user_token()
        if not token:
            print("❌ 错误: 无法获取 User Token")
            return None
        
        list_url = "https://open.teambition.com/api/v3/project/priority/list"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        params = {"organizationId": organization_id}
        
        print(f"正在查询企业 {organization_id} 的优先级列表...")
        response = requests.get(list_url, headers=headers, params=params)
        
        if response.status_code == 200:
            result = response.json()
            return result.get('result', [])
        else:
            error_msg = f"查询失败，状态码: {response.status_code}"
            try:
                error_detail = response.json()
                error_msg += f", 错误信息: {json.dumps(error_detail, ensure_ascii=False)}"
            except:
                error_msg += f", 响应内容: {response.text}"
            print(f"❌ {error_msg}")
            return None
            
    except Exception as e:
        print(f"❌ 发生异常: {str(e)}")
        return None

def main():
    """主函数"""
    if len(sys.argv) < 2 or sys.argv[1] == "--help":
        print("用法: uv run scripts/get-priority-list.py <组织ID>")
        print("")
        print("参数:")
        print("  组织ID: Teambition 企业/组织 ID")
        print("")
        print("说明:")
        print("  获取企业配置的任务优先级列表。不同企业可能有不同的优先级配置。")
        print("  组织 ID 可以从项目信息中获取（project.organizationId）。")
        print("")
        print("示例:")
        print("  uv run scripts/get-priority-list.py 67ec9b8c3c6130ac88605c3e")
        sys.exit(0 if len(sys.argv) >= 2 and sys.argv[1] == "--help" else 1)
    
    organization_id = sys.argv[1]
    
    priority_list = get_priority_list(organization_id)
    
    if priority_list is not None:
        print(f"\n✅ 查询成功！共 {len(priority_list)} 个优先级配置：\n")
        print("  ┌─────────┬─────────┬──────────────┐")
        print("  │  值     │  名称   │  默认选项    │")
        print("  ├─────────┼─────────┼──────────────┤")
        for item in priority_list:
            name = item.get('name', 'N/A')
            priority = item.get('priority', 'N/A')
            is_default = "是" if item.get('isDefault') else "否"
            print(f"  │   {priority:<4}  │  {name:<5} │  {is_default:<10} │")
        print("  └─────────┴─────────┴──────────────┘")
        
        # 输出 JSON 格式
        print("\n完整数据 (JSON):")
        print(json.dumps(priority_list, ensure_ascii=False, indent=2))
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
