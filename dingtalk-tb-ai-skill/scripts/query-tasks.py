#!/usr/bin/env python3
"""
Teambition 查询任务脚本
调用 call-user-api 脚本查询任务
"""

import subprocess
import sys
import json
from typing import Optional, List, Dict, Any

def query_task_details(task_ids: List[str]) -> Optional[List[Dict[str, Any]]]:
    """
    查询任务详情
    
    Args:
        task_ids: 任务ID列表
        
    Returns:
        任务详情列表，失败返回 None
    """
    if not task_ids:
        return []
    
    # 构建任务ID字符串
    task_ids_str = ",".join(task_ids)
    
    # 调用 query-tasks-detail.py 脚本查询任务详情（简单模式）
    try:
        result = subprocess.run(
            ["uv", "run", "scripts/query-tasks-detail.py", task_ids_str, "--detail-level", "simple"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            # 从输出中提取 JSON 内容
            output = result.stdout
            
            # 查找最后一个 JSON 数组（任务详情列表）
            lines = output.strip().split('\n')
            json_lines = []
            in_json = False
            bracket_count = 0
            
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('['):
                    in_json = True
                    bracket_count = stripped.count('[') - stripped.count(']')
                    json_lines = [line]
                elif in_json:
                    json_lines.append(line)
                    bracket_count += stripped.count('[') - stripped.count(']')
                    if bracket_count == 0:
                        break
            
            if json_lines:
                try:
                    tasks = json.loads('\n'.join(json_lines))
                    return tasks
                except json.JSONDecodeError:
                    pass
        
        return None
        
    except Exception:
        return None

def query_tasks(tql: Optional[str] = None, page_size: Optional[int] = None, 
                page_token: Optional[str] = None, fetch_details: bool = True):
    """
    查询 Teambition 任务
    
    Args:
        tql: 任务查询语言（可选）
        page_size: 每页大小（可选）
        page_token: 分页令牌（可选）
        fetch_details: 是否自动获取任务详情（默认 True）
    """
    # 构建查询参数
    params = {}
    if tql:
        params["tql"] = tql
    if page_size:
        params["pageSize"] = page_size
    if page_token:
        params["pageToken"] = page_token
    
    # 构建查询字符串
    query_string = ""
    if params:
        query_string = "?" + "&".join([f"{k}={v}" for k, v in params.items()])
    
    # API 路径
    api_path = f"/v2/all-task/search{query_string}"
    
    print(f"正在查询任务...")
    if tql:
        print(f"  TQL: {tql}")
    if page_size:
        print(f"  每页大小: {page_size}")
    if page_token:
        print(f"  分页令牌: {page_token}")
    
    # 调用 call-user-api 脚本
    try:
        result = subprocess.run(
            ["uv", "run", "scripts/call-user-api.py", "GET", api_path],
            capture_output=True,
            text=True,
            check=False
        )
        
        # 输出搜索结果
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        if result.returncode != 0:
            return False
        
        # 如果需要获取详情，解析任务ID并查询详情
        if fetch_details:
            # 从输出中提取任务ID列表
            output = result.stdout
            response_marker = "响应:"
            
            if response_marker in output:
                json_start = output.index(response_marker) + len(response_marker)
                json_content = output[json_start:].strip()
                
                try:
                    # 解析 JSON - 这是 API 的原始响应
                    api_response = json.loads(json_content)
                    
                    # 提取任务ID列表
                    task_ids = []
                    if api_response.get("code") == 200 and "result" in api_response:
                        if api_response["result"]:
                            task_ids = api_response["result"]
                    
                    # 如果有任务ID，查询详情
                    if task_ids:
                        print(f"\n正在获取 {len(task_ids)} 个任务的详细信息...")
                        task_details = query_task_details(task_ids)
                        
                        if task_details:
                            print("\n" + "="*50)
                            print(f"✅ 任务详情获取成功！")
                            print("="*50)
                            print(json.dumps(task_details, ensure_ascii=False, indent=2))
                        else:
                            print("\n⚠️  获取任务详情失败")
                    
                except json.JSONDecodeError:
                    pass
        
        return True
        
    except FileNotFoundError:
        print("❌ 错误: 找不到 call-user-api.py 脚本")
        print("请确保该脚本在 scripts 目录下")
        return False
    except Exception as e:
        print(f"❌ 发生异常: {str(e)}")
        return False

def main():
    """主函数 - 命令行入口"""
    # 解析参数
    tql = None
    page_size = None
    page_token = None
    fetch_details = True
    
    # 如果没有参数或只有 --help，显示帮助信息
    if len(sys.argv) < 2:
        query_tasks(tql, page_size, page_token, fetch_details)
        return
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg == "--tql" and i + 1 < len(sys.argv):
            tql = sys.argv[i + 1]
            i += 2
        elif arg == "--page-size" and i + 1 < len(sys.argv):
            try:
                page_size = int(sys.argv[i + 1])
                i += 2
            except ValueError:
                print("❌ 错误: --page-size 必须是整数")
                sys.exit(1)
        elif arg == "--page-token" and i + 1 < len(sys.argv):
            page_token = sys.argv[i + 1]
            i += 2
        elif arg == "--no-details":
            fetch_details = False
            i += 1
        elif arg == "--help":
            print("用法: uv run scripts/query-tasks.py [选项]")
            print("\n选项:")
            print("  --tql <TQL>              任务查询语言（可选）")
            print("  --page-size <大小>      每页大小（可选）")
            print("  --page-token <令牌>     分页令牌（可选）")
            print("  --no-details            不自动获取任务详情（默认会自动获取）")
            print("  --help                  显示此帮助信息")
            print("\n示例:")
            print("  # 查询所有任务（自动获取详情）")
            print("  uv run scripts/query-tasks.py")
            print("")
            print("  # 使用 TQL 查询")
            print('  uv run scripts/query-tasks.py --tql "status=done"')
            print("")
            print("  # 设置每页大小")
            print("  uv run scripts/query-tasks.py --page-size 50")
            print("")
            print("  # 只查询任务ID，不获取详情")
            print("  uv run scripts/query-tasks.py --no-details")
            print("")
            print("  # 使用分页令牌")
            print('  uv run scripts/query-tasks.py --page-token "xxx"')
            print("")
            print("  # 组合使用")
            print('  uv run scripts/query-tasks.py --tql "status=doing" --page-size 20')
            sys.exit(0)
        else:
            print(f"❌ 错误: 未知参数 {arg}")
            sys.exit(1)
    
    # 执行查询
    success = query_tasks(tql, page_size, page_token, fetch_details)
    
    # 根据结果退出
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
