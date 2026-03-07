#!/usr/bin/env python3
"""
Teambition 查询任务详情脚本
调用 call-user-api 脚本查询任务详情
"""

import subprocess
import sys
import json
from typing import Optional, List, Dict, Any

def format_simple_task(task: Dict[str, Any], extra_fields: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    格式化任务为简单信息
    
    Args:
        task: 完整的任务信息
        extra_fields: 额外需要包含的字段列表（可选）
        
    Returns:
        简化后的任务信息
    """
    # 默认简单字段
    simple_task = {
        "id": task.get("id"),
        "content": task.get("content"),
        "isDone": task.get("isDone"),
        "executorId": task.get("executorId"),
        "projectId": task.get("projectId"),
        "dueDate": task.get("dueDate"),
        "priority": task.get("priority"),
        "created": task.get("created"),
        "updated": task.get("updated")
    }
    
    # 如果指定了额外字段，追加这些字段
    if extra_fields:
        for field in extra_fields:
            if field in task and field not in simple_task:
                simple_task[field] = task.get(field)
    
    return simple_task

def query_tasks_detail(task_ids: str, detail_level: str = "simple", extra_fields: Optional[List[str]] = None):
    """
    查询 Teambition 任务详情
    
    Args:
        task_ids: 任务ID集合，使用逗号分隔
        detail_level: 详细程度，"simple" 或 "detailed"，默认 "simple"
        extra_fields: 简单模式下额外需要包含的字段列表（可选）
    """
    # 构建查询参数
    query_string = f"?taskId={task_ids}"
    
    # API 路径
    api_path = f"/v3/task/query{query_string}"
    
    print(f"正在查询任务详情...")
    print(f"  任务ID: {task_ids}")
    print(f"  详细程度: {detail_level}")
    if extra_fields:
        print(f"  额外字段: {', '.join(extra_fields)}")
    
    # 调用 call-user-api 脚本
    try:
        result = subprocess.run(
            ["uv", "run", "scripts/call-user-api.py", "GET", api_path],
            capture_output=True,
            text=True,
            check=False
        )
        
        # 解析结果
        if result.returncode == 0:
            # 从输出中提取 "响应:" 后面的 JSON 内容
            output = result.stdout
            
            # 查找 "响应:" 标记
            response_marker = "响应:"
            if response_marker in output:
                # 提取响应标记之后的内容
                json_start = output.index(response_marker) + len(response_marker)
                json_content = output[json_start:].strip()
                
                try:
                    # 解析 JSON - 这是 API 的原始响应
                    api_response = json.loads(json_content)
                    
                    # API 原始响应格式: {"code": 200, "result": [...]}
                    if api_response.get("code") == 200 and "result" in api_response:
                        tasks = api_response["result"]

                        # 检查是否为空
                        if not tasks:
                            print("\n" + "="*50)
                            print("⚠️  未找到任何任务")
                            print("="*50)
                            return True
                        
                        # 根据 detail_level 处理任务信息
                        if detail_level == "simple":
                            tasks = [format_simple_task(task, extra_fields) for task in tasks]
                        
                        # 输出格式化的结果
                        print("\n" + "="*50)
                        print(f"✅ 查询成功！共找到 {len(tasks)} 个任务")
                        print("="*50)
                        print(json.dumps(tasks, ensure_ascii=False, indent=2))
                        return True
                    else:
                        # API 响应中没有 result 字段或状态码不是 200
                        print("\n" + "="*50)
                        print("❌ API 响应格式异常或请求失败")
                        print("="*50)
                        print(json.dumps(api_response, ensure_ascii=False, indent=2))
                        return False
                        
                except json.JSONDecodeError as e:
                    # JSON 解析失败，输出原始内容
                    print("\n" + "="*50)
                    print("❌ 响应解析失败")
                    print("="*50)
                    print(f"JSON 解析错误: {str(e)}")
                    print(f"原始响应内容:\n{json_content}")
                    return False
            else:
                # 没有找到响应标记，直接输出原始结果
                print(output)
                return True
        else:
            # subprocess 执行失败
            print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            return False
        
    except FileNotFoundError:
        print("❌ 错误: 找不到 call-user-api.py 脚本")
        print("请确保该脚本在 scripts 目录下")
        return False
    except Exception as e:
        print(f"❌ 发生异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数 - 命令行入口"""
    # 如果没有参数或只有 --help，显示帮助信息
    if len(sys.argv) < 2 or "--help" in sys.argv:
        print("用法: uv run scripts/query-tasks-detail.py <任务ID> [选项]")
        print("\n参数:")
        print("  任务ID                   任务ID集合，使用逗号分隔（必需）")
        print("\n选项:")
        print("  --detail-level <级别>   详细程度: simple(简单) 或 detailed(详细)")
        print("                          默认: simple")
        print("  --extra-fields <字段>   简单模式下额外包含的字段，使用逗号分隔")
        print("                          例如: note,sprintId,stageId")
        print("  --help                  显示此帮助信息")
        print("\n示例:")
        print("  # 查询单个任务（简单信息）")
        print("  uv run scripts/query-tasks-detail.py 67ec9b8c3c6130ac88605c3e")
        print("")
        print("  # 查询多个任务（简单信息）")
        print("  uv run scripts/query-tasks-detail.py 67ec9b8c3c6130ac88605c3e,67ec9b8c3c6130ac88605c3f")
        print("")
        print("  # 查询任务详细信息")
        print("  uv run scripts/query-tasks-detail.py 67ec9b8c3c6130ac88605c3e --detail-level detailed")
        print("")
        print("  # 简单模式追加额外字段")
        print("  uv run scripts/query-tasks-detail.py 67ec9b8c3c6130ac88605c3e --extra-fields note,sprintId")
        print("")
        print("简单信息默认包含字段:")
        print("  - id: 任务ID")
        print("  - content: 任务标题")
        print("  - isDone: 是否完成")
        print("  - executorId: 执行人ID")
        print("  - projectId: 项目ID")
        print("  - dueDate: 截止时间")
        print("  - priority: 优先级")
        print("  - created: 创建时间")
        print("  - updated: 更新时间")
        print("")
        print("详细信息包含所有 API 返回的字段")
        sys.exit(0)
    
    # 解析参数
    task_ids = sys.argv[1]
    detail_level = "simple"
    extra_fields = None
    
    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg == "--detail-level" and i + 1 < len(sys.argv):
            detail_level = sys.argv[i + 1]
            if detail_level not in ["simple", "detailed"]:
                print(f"❌ 错误: --detail-level 必须是 'simple' 或 'detailed'")
                sys.exit(1)
            i += 2
        elif arg == "--extra-fields" and i + 1 < len(sys.argv):
            extra_fields = [f.strip() for f in sys.argv[i + 1].split(',')]
            i += 2
        else:
            print(f"❌ 错误: 未知参数 {arg}")
            sys.exit(1)
    
    # 执行查询
    success = query_tasks_detail(task_ids, detail_level, extra_fields)
    
    # 根据结果退出
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
