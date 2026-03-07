#!/usr/bin/env python3
"""
更新 Teambition 任务优先级脚本
调用 /v3/task/{taskId}/priority 接口更新任务优先级
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

def update_task_priority(task_id, priority):
    """
    更新任务优先级
    
    Args:
        task_id: 任务 ID
        priority: 优先级值（整数）
    
    Returns:
        bool: 是否成功
    """
    try:
        token = load_user_token()
        if not token:
            print("❌ 错误: 无法获取 User Token")
            return False
        
        update_url = f"https://open.teambition.com/api/v3/task/{task_id}/priority"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        data = {"priority": priority}
        
        print(f"正在更新任务 {task_id} 的优先级为 {priority}...")
        
        response = requests.put(update_url, headers=headers, data=json.dumps(data))
        
        if response.status_code == 200:
            print(f"✅ 任务优先级更新成功！")
            return True
        else:
            error_msg = f"更新失败，状态码: {response.status_code}"
            try:
                error_detail = response.json()
                error_msg += f", 错误信息: {json.dumps(error_detail, ensure_ascii=False)}"
            except:
                error_msg += f", 响应内容: {response.text}"
            print(f"❌ {error_msg}")
            return False
            
    except Exception as e:
        print(f"❌ 发生异常: {str(e)}")
        return False

def main():
    """主函数"""
    if len(sys.argv) < 2 or sys.argv[1] == "--help":
        print("用法: uv run scripts/user-update-task-priority.py <任务ID> <优先级>")
        print("")
        print("参数:")
        print("  任务ID: Teambition 任务 ID")
        print("  优先级: 优先级值（整数）")
        print("")
        print("说明:")
        print("  企业可以自定义优先级映射，直接传入对应的优先级数值即可")
        print("")
        print("示例:")
        print("  uv run scripts/user-update-task-priority.py 69a13167f367e8c8a5e70d39 3")
        print("")
        print("提示:")
        print("  - 更新前建议先查询企业优先级配置: uv run scripts/get-priority-list.py <组织ID>")
        sys.exit(0 if len(sys.argv) >= 2 and sys.argv[1] == "--help" else 1)
    
    if len(sys.argv) < 3:
        print("❌ 错误: 缺少参数")
        print("用法: uv run scripts/user-update-task-priority.py <任务ID> <优先级>")
        print("使用 --help 查看帮助信息")
        sys.exit(1)
    
    task_id = sys.argv[1]
    priority_input = sys.argv[2]
    
    # 解析优先级（支持任意整数）
    try:
        priority = int(priority_input)
    except ValueError:
        print(f"❌ 无效的优先级: {priority_input}，请输入有效的整数")
        sys.exit(1)
    
    # 更新优先级
    success = update_task_priority(task_id, priority)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()