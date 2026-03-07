#!/usr/bin/env python3
"""
Teambition 获取项目工作流状态脚本
调用 /v3/project/{projectId}/taskflowstatus/search 接口获取项目的工作流状态列表
"""

import subprocess
import sys
import json
from typing import Optional, List, Dict, Any

def get_taskflow_statuses(project_id: str, 
                         taskflow_id: Optional[str] = None,
                         q: Optional[str] = None,
                         only_start: bool = False) -> Optional[List[Dict[str, Any]]]:
    """
    获取项目的工作流状态列表
    
    Args:
        project_id: 项目 ID（必需）
        taskflow_id: 工作流 ID（可选）
        q: 根据名称搜索状态（可选，支持模糊匹配）
        only_start: 是否只返回 kind=start 的状态（可选）
        
    Returns:
        工作流状态列表，失败返回 None
    """
    # 构建查询参数
    query_params = []
    if taskflow_id:
        query_params.append(f"tfIds={taskflow_id}")
    if q:
        query_params.append(f"q={q}")
    
    query_string = f"?{'&'.join(query_params)}" if query_params else ""
    
    # API 路径
    api_path = f"v3/project/{project_id}/taskflowstatus/search{query_string}"
    
    print(f"正在获取项目工作流状态...")
    print(f"  项目 ID: {project_id}")
    if taskflow_id:
        print(f"  工作流 ID: {taskflow_id}")
    if q:
        print(f"  搜索关键词: {q}")
    if only_start:
        print(f"  仅返回可用于创建任务的状态 (kind=start)")
    
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
                        statuses = api_response["result"]
                        
                        # 检查是否为空
                        if not statuses:
                            print("\n" + "="*50)
                            print("⚠️  未找到任何工作流状态")
                            print("="*50)
                            return []
                        
                        # 如果只返回 kind=start 的状态
                        if only_start:
                            statuses = [s for s in statuses if s.get("kind") == "start"]
                            if not statuses:
                                print("\n" + "="*50)
                                print("⚠️  未找到 kind=start 的状态")
                                print("="*50)
                                return []
                        
                        # 输出格式化的结果
                        print("\n" + "="*50)
                        print(f"✅ 查询成功！共找到 {len(statuses)} 个工作流状态")
                        print("="*50)
                        
                        for idx, status in enumerate(statuses, 1):
                            print(f"\n【状态 {idx}】")
                            print(f"  ID: {status.get('id')}")
                            print(f"  名称: {status.get('name')}")
                            print(f"  类型: {status.get('kind', 'N/A')}")
                            print(f"  工作流ID: {status.get('taskflowId', 'N/A')}")
                            print(f"  排序: {status.get('pos', 'N/A')}")
                            
                            # 标记是否可用于创建任务
                            if status.get('kind') == 'start':
                                print(f"  ✓ 可用于创建任务")
                        
                        print("\n完整信息:")
                        print(json.dumps(statuses, ensure_ascii=False, indent=2))
                        
                        return statuses
                    else:
                        # API 响应中没有 result 字段或状态码不是 200
                        print("\n" + "="*50)
                        print("❌ API 响应格式异常或请求失败")
                        print("="*50)
                        print(json.dumps(api_response, ensure_ascii=False, indent=2))
                        return None
                        
                except json.JSONDecodeError as e:
                    # JSON 解析失败，输出原始内容
                    print("\n" + "="*50)
                    print("❌ 响应解析失败")
                    print("="*50)
                    print(f"JSON 解析错误: {str(e)}")
                    print(f"原始响应内容:\n{json_content}")
                    return None
            else:
                # 没有找到响应标记，直接输出原始结果
                print(output)
                return None
        else:
            # subprocess 执行失败
            print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            return None
        
    except FileNotFoundError:
        print("❌ 错误: 找不到 call-user-api.py 脚本")
        print("请确保该脚本在 scripts 目录下")
        return None
    except Exception as e:
        print(f"❌ 发生异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """主函数 - 命令行入口"""
    # 如果没有参数或只有 --help，显示帮助信息
    if len(sys.argv) < 2 or "--help" in sys.argv:
        print("用法: uv run scripts/get-taskflow-statuses.py <项目ID> [选项]")
        print("\n参数:")
        print("  项目ID                   项目 ID（必需）")
        print("\n选项:")
        print("  --taskflow-id <ID>      工作流 ID")
        print("  --q <关键词>            根据名称搜索（支持模糊匹配）")
        print("  --only-start            只返回可用于创建任务的状态 (kind=start)")
        print("  --help                  显示此帮助信息")
        print("\n示例:")
        print("  # 获取项目所有工作流状态")
        print("  uv run scripts/get-taskflow-statuses.py 67ec9b8c3c6130ac88605c3e")
        print("")
        print("  # 获取指定工作流的状态")
        print("  uv run scripts/get-taskflow-statuses.py 67ec9b8c3c6130ac88605c3e --taskflow-id 67ec9b8c3c6130ac88605c40")
        print("")
        print("  # 只获取可用于创建任务的状态")
        print("  uv run scripts/get-taskflow-statuses.py 67ec9b8c3c6130ac88605c3e --only-start")
        print("")
        print("  # 根据名称搜索状态")
        print("  uv run scripts/get-taskflow-statuses.py 67ec9b8c3c6130ac88605c3e --q '未开始'")
        sys.exit(0)
    
    # 解析参数
    project_id = sys.argv[1]
    taskflow_id = None
    q = None
    only_start = False
    
    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg == "--taskflow-id" and i + 1 < len(sys.argv):
            taskflow_id = sys.argv[i + 1]
            i += 2
        elif arg == "--q" and i + 1 < len(sys.argv):
            q = sys.argv[i + 1]
            i += 2
        elif arg == "--only-start":
            only_start = True
            i += 1
        else:
            print(f"❌ 错误: 未知参数 {arg}")
            sys.exit(1)
    
    # 执行查询
    result = get_taskflow_statuses(project_id, taskflow_id, q, only_start)
    
    # 根据结果退出
    if result is not None:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
