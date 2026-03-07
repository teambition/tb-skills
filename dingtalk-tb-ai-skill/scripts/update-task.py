#!/usr/bin/env python3
"""
Teambition 更新任务脚本
支持更新任务的各个字段，每个字段通过独立的 API 端点更新
支持并行执行多个更新操作以提高性能
"""

import subprocess
import sys
import json
import os
from typing import Optional, Dict, Any, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

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

def call_update_api(endpoint: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """调用更新 API"""
    try:
        token = load_user_token()
        if not token:
            print("❌ 无法获取 User Token")
            return None
        
        payload_json = json.dumps(payload, ensure_ascii=False)
        result = subprocess.run(
            ["uv", "run", "scripts/call-user-api.py", "PUT", endpoint, payload_json],
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
                        return api_response.get("result", api_response)
                    else:
                        print(f"❌ 更新失败: {api_response}")
                        return None
                except json.JSONDecodeError:
                    pass
        
        print(f"❌ API 调用失败: {endpoint}")
        print(result.stdout)
        return None
    except Exception as e:
        print(f"❌ 发生异常: {str(e)}")
        return None

def call_customfield_api(task_id: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """调用自定义字段更新 API（使用 POST 方法）"""
    try:
        token = load_user_token()
        if not token:
            print("❌ 无法获取 User Token")
            return None
        
        endpoint = f"v3/task/{task_id}/customfield/update"
        payload_json = json.dumps(payload, ensure_ascii=False)
        result = subprocess.run(
            ["uv", "run", "scripts/call-user-api.py", "POST", endpoint, payload_json],
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
                        return api_response.get("result", api_response)
                    else:
                        print(f"❌ 更新自定义字段失败: {api_response}")
                        return None
                except json.JSONDecodeError:
                    pass
        
        print(f"❌ 自定义字段 API 调用失败")
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

def execute_update(task_id: str, field_name: str, endpoint: str, payload: Dict[str, Any], is_customfield: bool = False) -> Tuple[str, bool, Optional[Dict[str, Any]]]:
    """执行单个字段的更新操作
    
    Returns:
        Tuple[field_name, success, result]
    """
    if is_customfield:
        result = call_customfield_api(task_id, payload)
    else:
        result = call_update_api(endpoint, payload)
    
    return (field_name, result is not None, result)

def update_task(task_id: str, updates: Dict[str, Any]) -> bool:
    """更新任务的各个字段，支持并行执行"""
    
    # 准备所有更新任务
    update_tasks: List[Tuple[str, str, Dict[str, Any], bool]] = []
    
    # 更新任务标题
    if 'content' in updates:
        update_tasks.append((
            "任务标题",
            f"v3/task/{task_id}/content",
            {"content": updates['content']},
            False
        ))
    
    # 更新执行人
    if 'executorId' in updates:
        update_tasks.append((
            "执行人",
            f"v3/task/{task_id}/executor",
            {"executorId": updates['executorId']},
            False
        ))
    
    # 更新截止日期
    if 'dueDate' in updates:
        update_tasks.append((
            "截止日期",
            f"v3/task/{task_id}/dueDate",
            {"dueDate": updates['dueDate']},
            False
        ))
    
    # 更新开始日期
    if 'startDate' in updates:
        update_tasks.append((
            "开始日期",
            f"v3/task/{task_id}/startDate",
            {"startDate": updates['startDate']},
            False
        ))
    
    # 更新备注
    if 'note' in updates:
        update_tasks.append((
            "任务备注",
            f"v3/task/{task_id}/note",
            {"note": updates['note']},
            False
        ))
    
    # 更新优先级
    if 'priority' in updates:
        update_tasks.append((
            "优先级",
            f"v3/task/{task_id}/priority",
            {"priority": updates['priority']},
            False
        ))
    
    # 更新故事点
    if 'storyPoint' in updates:
        update_tasks.append((
            "故事点",
            f"v3/task/{task_id}/storyPoint",
            {"storyPoint": updates['storyPoint']},
            False
        ))
    
    # 更新任务状态
    if 'taskflowstatusId' in updates:
        update_tasks.append((
            "任务状态",
            f"v3/task/{task_id}/taskflowstatus",
            {"taskflowstatusId": updates['taskflowstatusId']},
            False
        ))
    
    # 更新参与者
    if 'involveMembers' in updates or 'addInvolvers' in updates or 'delInvolvers' in updates:
        payload = {}
        if 'involveMembers' in updates:
            payload['involveMembers'] = updates['involveMembers']
        if 'addInvolvers' in updates:
            payload['addInvolvers'] = updates['addInvolvers']
        if 'delInvolvers' in updates:
            payload['delInvolvers'] = updates['delInvolvers']
        
        update_tasks.append((
            "参与者",
            f"v3/task/{task_id}/involveMembers",
            payload,
            False
        ))
    
    # 更新自定义字段
    if 'customfields' in updates:
        for idx, customfield in enumerate(updates['customfields']):
            update_tasks.append((
                f"自定义字段 #{idx + 1}",
                "",  # 自定义字段不需要 endpoint
                customfield,
                True
            ))
    
    total_count = len(update_tasks)
    if total_count == 0:
        return False
    
    print(f"\n开始并行更新 {total_count} 个字段...")
    
    # 使用线程池并行执行更新
    success_count = 0
    results = []
    
    with ThreadPoolExecutor(max_workers=min(total_count, 10)) as executor:
        # 提交所有任务
        future_to_field = {}
        for field_name, endpoint, payload, is_customfield in update_tasks:
            future = executor.submit(
                execute_update,
                task_id,
                field_name,
                endpoint,
                payload,
                is_customfield
            )
            future_to_field[future] = field_name
        
        # 收集结果
        for future in as_completed(future_to_field):
            field_name, success, result = future.result()
            results.append((field_name, success, result))
            
            if success:
                success_count += 1
                # 根据字段类型显示不同的成功信息
                if field_name == "任务标题" and result:
                    print(f"✅ {field_name}已更新: {result.get('content')}")
                elif field_name == "执行人" and result:
                    print(f"✅ {field_name}已更新: {result.get('executorId')}")
                elif field_name == "截止日期" and result:
                    print(f"✅ {field_name}已更新: {result.get('dueDate')}")
                elif field_name == "开始日期" and result:
                    print(f"✅ {field_name}已更新: {result.get('startDate')}")
                elif field_name == "优先级" and result:
                    print(f"✅ {field_name}已更新: {result.get('priority')}")
                elif field_name == "故事点" and result:
                    print(f"✅ {field_name}已更新: {result.get('storyPoint')}")
                elif field_name == "任务状态" and result:
                    print(f"✅ {field_name}已更新: {result.get('taskflowstatusId')}")
                else:
                    print(f"✅ {field_name}已更新")
            else:
                print(f"❌ {field_name}更新失败")
    
    print(f"\n更新完成: {success_count}/{total_count} 个字段成功")
    
    return success_count == total_count and total_count > 0

def main():
    """主函数"""
    if "--help" in sys.argv:
        print("用法: uv run scripts/update-task.py --task-id <任务ID> [选项]")
        print("\n必需参数:")
        print("  --task-id <ID>                任务 ID（必需）")
        print("\n可更新字段:")
        print("  --content <标题>              任务标题")
        print("  --executor-id <ID>            执行人 ID")
        print("  --due-date <日期>             截止日期（ISO 8601 格式）")
        print("  --start-date <日期>           开始日期（ISO 8601 格式）")
        print("  --note <备注>                 任务备注")
        print("  --priority <0-3>              优先级（0=紧急，1=高，2=中，3=低）")
        print("  --story-point <点数>          故事点")
        print("  --taskflowstatus-id <ID>      任务状态 ID")
        print("  --involve-members <JSON>      参与者 ID 列表（JSON 数组，完全替换）")
        print("  --add-involvers <JSON>        新增参与者 ID 列表（JSON 数组）")
        print("  --del-involvers <JSON>        移除参与者 ID 列表（JSON 数组）")
        print("  --customfields <JSON>         自定义字段（JSON 数组）")
        print("\n示例:")
        print("  # 更新任务标题")
        print("  uv run scripts/update-task.py \\")
        print("    --task-id '67f0a1b2c3d4e5f6g7h8i9j0' \\")
        print("    --content '新的任务标题'")
        print("")
        print("  # 更新多个字段")
        print("  uv run scripts/update-task.py \\")
        print("    --task-id '67f0a1b2c3d4e5f6g7h8i9j0' \\")
        print("    --content '更新后的标题' \\")
        print("    --executor-id '696f2c084a459842b42b035b' \\")
        print("    --due-date '2026-03-15T00:00:00.000Z' \\")
        print("    --priority 1 \\")
        print("    --note '更新后的备注'")
        print("")
        print("  # 更新参与者（增量）")
        print("  uv run scripts/update-task.py \\")
        print("    --task-id '67f0a1b2c3d4e5f6g7h8i9j0' \\")
        print("    --add-involvers '[\"user1\", \"user2\"]' \\")
        print("    --del-involvers '[\"user3\"]'")
        sys.exit(0)
    
    # 解析参数
    task_id = None
    updates = {}
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg == "--task-id" and i + 1 < len(sys.argv):
            task_id = sys.argv[i + 1]
            i += 2
        elif arg == "--content" and i + 1 < len(sys.argv):
            updates['content'] = sys.argv[i + 1]
            i += 2
        elif arg == "--executor-id" and i + 1 < len(sys.argv):
            updates['executorId'] = sys.argv[i + 1]
            i += 2
        elif arg == "--due-date" and i + 1 < len(sys.argv):
            updates['dueDate'] = sys.argv[i + 1]
            i += 2
        elif arg == "--start-date" and i + 1 < len(sys.argv):
            updates['startDate'] = sys.argv[i + 1]
            i += 2
        elif arg == "--note" and i + 1 < len(sys.argv):
            updates['note'] = sys.argv[i + 1]
            i += 2
        elif arg == "--priority" and i + 1 < len(sys.argv):
            try:
                updates['priority'] = int(sys.argv[i + 1])
                i += 2
            except ValueError:
                print("❌ 错误: --priority 必须是整数")
                sys.exit(1)
        elif arg == "--story-point" and i + 1 < len(sys.argv):
            updates['storyPoint'] = sys.argv[i + 1]
            i += 2
        elif arg == "--taskflowstatus-id" and i + 1 < len(sys.argv):
            updates['taskflowstatusId'] = sys.argv[i + 1]
            i += 2
        elif arg == "--involve-members" and i + 1 < len(sys.argv):
            updates['involveMembers'] = parse_json_field(sys.argv[i + 1])
            i += 2
        elif arg == "--add-involvers" and i + 1 < len(sys.argv):
            updates['addInvolvers'] = parse_json_field(sys.argv[i + 1])
            i += 2
        elif arg == "--del-involvers" and i + 1 < len(sys.argv):
            updates['delInvolvers'] = parse_json_field(sys.argv[i + 1])
            i += 2
        elif arg == "--customfields" and i + 1 < len(sys.argv):
            updates['customfields'] = parse_json_field(sys.argv[i + 1])
            i += 2
        else:
            print(f"❌ 错误: 未知参数 {arg}")
            print("使用 --help 查看帮助信息")
            sys.exit(1)
    
    # 验证必需参数
    if not task_id:
        print("❌ 错误: 缺少必需参数 --task-id")
        print("使用 --help 查看帮助信息")
        sys.exit(1)
    
    if not updates:
        print("❌ 错误: 至少需要指定一个要更新的字段")
        print("使用 --help 查看帮助信息")
        sys.exit(1)
    
    print("\n" + "="*50)
    print("Teambition 任务更新")
    print("="*50)
    print(f"任务 ID: {task_id}")
    print(f"更新字段数: {len([k for k in updates.keys() if k not in ['addInvolvers', 'delInvolvers']])}")
    print("="*50)
    
    # 更新任务
    success = update_task(task_id, updates)
    
    if success:
        print("\n" + "="*50)
        print("✅ 任务更新完成！")
        print("="*50)
        sys.exit(0)
    else:
        print("\n" + "="*50)
        print("❌ 任务更新失败或部分失败")
        print("="*50)
        sys.exit(1)

if __name__ == "__main__":
    main()
