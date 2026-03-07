#!/usr/bin/env python3
"""
Teambition 创建任务脚本
简化版本，直接调用 API 创建任务，支持核心字段
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
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('userToken')
        except Exception:
            pass
    
    return None

def create_task_api(task_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """调用 API 创建任务"""
    try:
        token = load_user_token()
        if not token:
            print("❌ 无法获取 User Token")
            return None
        
        # 构建请求体，只包含核心字段
        payload = {
            "content": task_data.get('content')  # 必填字段
        }
        
        # 添加可选字段
        optional_fields = [
            'projectId', 'executorId', 'involveMembers', 'taskflowstatusId',
            'startDate', 'dueDate', 'note', 'priority', 'parentTaskId',
            'progress', 'visible', 'storyPoint', 'scenariofieldconfigId', 'customfields'
        ]
        
        for field in optional_fields:
            if field in task_data and task_data[field] is not None:
                payload[field] = task_data[field]
        
        # 调用 API
        payload_json = json.dumps(payload, ensure_ascii=False)
        result = subprocess.run(
            ["uv", "run", "scripts/call-user-api.py", "POST", "v3/task/create", payload_json],
            capture_output=True,
            text=True,
            check=False
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
                        task = api_response.get("result", api_response)
                        print(f"\n✅ 任务创建成功！")
                        print(f"  任务 ID: {task.get('taskId')}")
                        print(f"  任务标题: {task.get('content')}")
                        if task.get('projectId'):
                            print(f"  项目 ID: {task.get('projectId')}")
                        if task.get('executorId'):
                            print(f"  执行人 ID: {task.get('executorId')}")
                        if task.get('dueDate'):
                            print(f"  截止日期: {task.get('dueDate')}")
                        return task
                    else:
                        print(f"❌ 创建失败: {api_response}")
                        return None
                except json.JSONDecodeError:
                    pass
        
        print("❌ 创建任务失败")
        print(result.stdout)
        return None
    except Exception as e:
        print(f"❌ 发生异常: {str(e)}")
        return None

def parse_json_field(value: str) -> Any:
    """解析 JSON 格式的字段值"""
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value

def main():
    """主函数"""
    if "--help" in sys.argv:
        print("用法: uv run scripts/create-task.py [选项]")
        print("\n必需参数:")
        print("  --content <标题>              任务标题（必需）")
        print("\n核心字段:")
        print("  --project-id <ID>             项目 ID")
        print("  --executor-id <ID>            执行人 ID")
        print("  --involve-members <JSON>      参与者 ID 列表（JSON 数组）")
        print("  --taskflowstatus-id <ID>      任务状态 ID")
        print("  --start-date <日期>           开始日期（ISO 8601 格式）")
        print("  --due-date <日期>             截止日期（ISO 8601 格式）")
        print("  --note <备注>                 任务备注")
        print("  --priority <0-3>              优先级（0=紧急，1=高，2=中，3=低）")
        print("  --parent-task-id <ID>         父任务 ID")
        print("  --progress <0-100>            进度")
        print("  --visible <类型>              可见性（involves=仅参与者，members=项目成员）")
        print("  --story-point <点数>          故事点")
        print("  --scenariofieldconfig-id <ID> 任务类型 ID")
        print("  --customfields <JSON>         自定义字段（JSON 数组）")
        print("\n示例:")
        print("  # 最简单创建")
        print("  uv run scripts/create-task.py \\")
        print("    --project-id '67ec9b8c3c6130ac88605c3e' \\")
        print("    --content '完成需求文档'")
        print("")
        print("  # 完整参数")
        print("  uv run scripts/create-task.py \\")
        print("    --project-id '67ec9b8c3c6130ac88605c3e' \\")
        print("    --content '实现用户管理' \\")
        print("    --executor-id '696f2c084a459842b42b035b' \\")
        print("    --due-date '2026-03-15T00:00:00.000Z' \\")
        print("    --priority 1 \\")
        print("    --note '需要实现增删改查功能'")
        print("")
        print("详细的字段说明和转换指引请参考: docs/create-task.md")
        sys.exit(0)
    
    # 解析参数
    task_data = {}
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg == "--content" and i + 1 < len(sys.argv):
            task_data['content'] = sys.argv[i + 1]
            i += 2
        elif arg == "--project-id" and i + 1 < len(sys.argv):
            task_data['projectId'] = sys.argv[i + 1]
            i += 2
        elif arg == "--executor-id" and i + 1 < len(sys.argv):
            task_data['executorId'] = sys.argv[i + 1]
            i += 2
        elif arg == "--involve-members" and i + 1 < len(sys.argv):
            task_data['involveMembers'] = parse_json_field(sys.argv[i + 1])
            i += 2
        elif arg == "--taskflowstatus-id" and i + 1 < len(sys.argv):
            task_data['taskflowstatusId'] = sys.argv[i + 1]
            i += 2
        elif arg == "--start-date" and i + 1 < len(sys.argv):
            task_data['startDate'] = sys.argv[i + 1]
            i += 2
        elif arg == "--due-date" and i + 1 < len(sys.argv):
            task_data['dueDate'] = sys.argv[i + 1]
            i += 2
        elif arg == "--note" and i + 1 < len(sys.argv):
            task_data['note'] = sys.argv[i + 1]
            i += 2
        elif arg == "--priority" and i + 1 < len(sys.argv):
            try:
                task_data['priority'] = int(sys.argv[i + 1])
                i += 2
            except ValueError:
                print("❌ 错误: --priority 必须是整数")
                sys.exit(1)
        elif arg == "--parent-task-id" and i + 1 < len(sys.argv):
            task_data['parentTaskId'] = sys.argv[i + 1]
            i += 2
        elif arg == "--progress" and i + 1 < len(sys.argv):
            try:
                task_data['progress'] = int(sys.argv[i + 1])
                i += 2
            except ValueError:
                print("❌ 错误: --progress 必须是整数")
                sys.exit(1)
        elif arg == "--visible" and i + 1 < len(sys.argv):
            task_data['visible'] = sys.argv[i + 1]
            i += 2
        elif arg == "--story-point" and i + 1 < len(sys.argv):
            task_data['storyPoint'] = sys.argv[i + 1]
            i += 2
        elif arg == "--scenariofieldconfig-id" and i + 1 < len(sys.argv):
            task_data['scenariofieldconfigId'] = sys.argv[i + 1]
            i += 2
        elif arg == "--customfields" and i + 1 < len(sys.argv):
            task_data['customfields'] = parse_json_field(sys.argv[i + 1])
            i += 2
        else:
            print(f"❌ 错误: 未知参数 {arg}")
            print("使用 --help 查看帮助信息")
            sys.exit(1)
    
    # 验证必需参数
    if 'content' not in task_data:
        print("❌ 错误: 缺少必需参数 --content")
        print("使用 --help 查看帮助信息")
        sys.exit(1)
    
    print("\n" + "="*50)
    print("Teambition 任务创建")
    print("="*50)
    print(f"任务标题: {task_data['content']}")
    if 'projectId' in task_data:
        print(f"项目 ID: {task_data['projectId']}")
    print("="*50)
    
    # 创建任务
    task = create_task_api(task_data)
    
    if task:
        print("\n" + "="*50)
        print("✅ 任务创建完成！")
        print("="*50)
        sys.exit(0)
    else:
        print("\n" + "="*50)
        print("❌ 任务创建失败")
        print("="*50)
        sys.exit(1)

if __name__ == "__main__":
    main()
