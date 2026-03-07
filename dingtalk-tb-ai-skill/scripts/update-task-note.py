#!/usr/bin/env python3
"""
Teambition 更新任务备注脚本
调用 PUT /v3/task/{taskId}/note 接口更新任务的备注信息
"""

import subprocess
import sys
import json
import os
from typing import Optional, Dict, Any

def load_user_token() -> Optional[str]:
    """加载 User Token"""
    token = os.environ.get("TB_USER_TOKEN")
    if token:
        return token
    
    config_file = "user-token.json"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_paths = [
        os.path.join(os.getcwd(), config_file),
        os.path.join(script_dir, config_file),
        os.path.join(script_dir, "..", config_file),
        config_file
    ]
    
    for config_path in config_paths:
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    token = config.get('userToken')
                    if token:
                        return token
            except Exception:
                pass
    
    return None

def get_task_info(task_id: str) -> Optional[Dict[str, Any]]:
    """获取任务的当前信息"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        
        result = subprocess.run(
            ["uv", "run", "scripts/query-tasks-detail.py", task_id, "--detail-level", "detailed", "--extra-fields", "note"],
            capture_output=True,
            text=True,
            check=False,
            cwd=project_root
        )
        if result.returncode == 0:
            output = result.stdout
            # 尝试两种解析方式：
            # 1. 从 "响应:" 标记后提取 JSON
            # 2. 直接查找 JSON 数组
            json_content = None
            
            response_marker = "响应:"
            if response_marker in output:
                json_start = output.index(response_marker) + len(response_marker)
                json_content = output[json_start:].strip()
            else:
                # 尝试查找 JSON 数组的起始位置
                json_array_start = output.find('[')
                if json_array_start != -1:
                    json_content = output[json_array_start:].strip()
            
            if json_content:
                try:
                    api_response = json.loads(json_content)
                    # 处理两种可能的响应格式：
                    # 1. 直接是任务列表 [{"id": ...}]
                    # 2. 包裹在 API 响应中 {"code": 200, "result": [...]}
                    tasks = None
                    if isinstance(api_response, list):
                        tasks = api_response
                    elif isinstance(api_response, dict):
                        if api_response.get("code") == 200 and "result" in api_response:
                            tasks = api_response["result"]
                    
                    if tasks and isinstance(tasks, list) and len(tasks) > 0:
                        return tasks[0]
                except json.JSONDecodeError:
                    pass
        
        return None
    except Exception as e:
        print(f"❌ 获取任务信息异常: {str(e)}")
        return None

def update_task_note(task_id: str, note: str) -> bool:
    """
    更新任务备注
    
    Args:
        task_id: 任务 ID
        note: 新的备注内容
        
    Returns:
        bool: 是否成功
    """
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        
        # 构建请求体
        payload = {
            "note": note
        }
        
        payload_json = json.dumps(payload, ensure_ascii=False)
        api_path = f"v3/task/{task_id}/note"
        
        result = subprocess.run(
            ["uv", "run", "scripts/call-user-api.py", "PUT", api_path, payload_json],
            capture_output=True,
            text=True,
            check=False,
            cwd=project_root
        )
        
        if result.returncode == 0:
            output = result.stdout
            response_marker = "响应:"
            if response_marker in output:
                json_start = output.index(response_marker) + len(response_marker)
                json_content = output[json_start:].strip()
                try:
                    api_response = json.loads(json_content)
                    if api_response.get("code") == 200:
                        return True
                    else:
                        print(f"❌ 更新失败: {api_response.get('errorMessage', '未知错误')}")
                        return False
                except json.JSONDecodeError:
                    pass
        
        print("❌ 更新任务备注失败")
        print(result.stdout)
        return False
    except Exception as e:
        print(f"❌ 发生异常: {str(e)}")
        return False

def main():
    """主函数"""
    if "--help" in sys.argv or len(sys.argv) < 3:
        print("用法: uv run scripts/update-task-note.py <任务ID> <备注内容>")
        print("\n参数:")
        print("  任务ID                   任务 ID（必需）")
        print("  备注内容                 新的任务备注（必需）")
        print("\n选项:")
        print("  --help                  显示此帮助信息")
        print("\n说明:")
        print("  此脚本用于更新任务的备注信息")
        print("  备注内容支持多行文本，将直接覆盖原有备注")
        print("  如果新备注与原备注完全相同，将跳过更新")
        print("\n示例:")
        print("  # 更新任务备注")
        print("  uv run scripts/update-task-note.py 67ec9b8c3c6130ac88605c3e '这是任务的备注内容'")
        print("")
        print("  # 备注内容包含空格时使用引号")
        print("  uv run scripts/update-task-note.py 67ec9b8c3c6130ac88605c3e '需要实现增删改查功能'")
        print("")
        print("相关脚本:")
        print("  query-tasks-detail.py      查询任务详情")
        print("  create-task.py             创建任务（可设置初始备注）")
        sys.exit(0)
    
    # 解析参数
    task_id = sys.argv[1]
    note = sys.argv[2]
    
    print("\n" + "="*50)
    print("Teambition 任务备注更新")
    print("="*50)
    print(f"任务 ID: {task_id}")
    
    # 获取任务当前信息
    print(f"\n正在获取任务信息...")
    current_task = get_task_info(task_id)
    if current_task:
        print(f"  任务标题: {current_task.get('content', 'N/A')}")
        current_note = current_task.get('note', '') or ''
        if current_note:
            print(f"  当前备注: {current_note[:100]}{'...' if len(current_note) > 100 else ''}")
        else:
            print(f"  当前备注: (无)")
        
        # 检查备注是否相同
        if current_note == note:
            print(f"\n新备注内容: {note[:100]}{'...' if len(note) > 100 else ''}")
            print("="*50)
            print("\n" + "="*50)
            print("ℹ️  新备注与当前备注完全相同，无需更新")
            print("="*50)
            sys.exit(0)
    else:
        print(f"  ⚠️  无法获取任务信息，继续执行更新...")
    
    print(f"\n新备注内容: {note[:100]}{'...' if len(note) > 100 else ''}")
    print("="*50)
    
    # 更新任务备注
    success = update_task_note(task_id, note)
    
    if success:
        print("\n" + "="*50)
        print("✅ 任务备注更新成功！")
        print("="*50)
        sys.exit(0)
    else:
        print("\n" + "="*50)
        print("❌ 任务备注更新失败")
        print("="*50)
        sys.exit(1)

if __name__ == "__main__":
    main()