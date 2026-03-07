#!/usr/bin/env python3
"""
Teambition 查询项目脚本
调用 call-user-api 脚本查询项目
"""

import subprocess
import sys
import json
from typing import Optional, List, Dict, Any

def query_project_details(project_ids: List[str]) -> Optional[List[Dict[str, Any]]]:
    """
    查询项目详情
    
    Args:
        project_ids: 项目ID列表
        
    Returns:
        项目详情列表（简单信息），失败返回 None
    """
    if not project_ids:
        return []
    
    # 构建项目ID字符串
    project_ids_str = ",".join(project_ids)
    
    # 调用 query-projects-detail.py 脚本查询项目详情（简单模式）
    try:
        result = subprocess.run(
            ["uv", "run", "scripts/query-projects-detail.py", project_ids_str, "--detail-level", "simple"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            # 从输出中提取 JSON 内容
            output = result.stdout
            
            # 查找最后一个 JSON 数组（项目详情列表）
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
                    projects = json.loads('\n'.join(json_lines))
                    return projects
                except json.JSONDecodeError:
                    pass
        
        return None
        
    except Exception:
        return None

def query_projects(tql: Optional[str] = None, page_size: Optional[int] = None, 
                   page_token: Optional[str] = None, include_template: bool = False,
                   fetch_details: bool = True):
    """
    查询 Teambition 项目
    
    Args:
        tql: 项目查询语言（可选）
        page_size: 每页大小（可选）
        page_token: 分页令牌（可选）
        include_template: 是否包含模板项目（默认 False）
        fetch_details: 是否自动获取项目详情（默认 True）
    """
    # 构建查询参数
    params = {}
    
    # 默认排除模板项目（除非用户明确要求包含）
    if tql:
        # 检查 TQL 中是否已经指定了 isTemplate（不区分大小写）
        tql_lower = tql.lower()
        has_istemplate = "istemplate" in tql_lower
        
        if not has_istemplate:
            # 提取 ORDER BY 子句（如果存在）
            order_by_clause = ""
            tql_without_order = tql
            
            # 查找 ORDER BY（不区分大小写）
            import re
            order_by_match = re.search(r'\s+ORDER\s+BY\s+.+$', tql, re.IGNORECASE)
            if order_by_match:
                order_by_clause = order_by_match.group(0)
                tql_without_order = tql[:order_by_match.start()]
            
            # 构建新的 TQL
            if tql_without_order.strip():
                tql = f"isTemplate = false AND ({tql_without_order}){order_by_clause}"
            else:
                tql = f"isTemplate = false{order_by_clause}"
        
        params["tql"] = tql
    else:
        # 如果没有提供 TQL，默认排除模板项目
        if not include_template:
            params["tql"] = "isTemplate = false"
    
    if page_size:
        params["pageSize"] = page_size
    if page_token:
        params["pageToken"] = page_token
    if include_template:
        params["includeTemplate"] = "true"
    
    # 构建查询字符串
    query_string = ""
    if params:
        query_string = "?" + "&".join([f"{k}={v}" for k, v in params.items()])
    
    # API 路径
    api_path = f"project/search{query_string}"
    
    print(f"正在查询项目...")
    if tql:
        print(f"  TQL: {tql}")
    if page_size:
        print(f"  每页大小: {page_size}")
    if page_token:
        print(f"  分页令牌: {page_token}")
    if include_template:
        print(f"  包含模板项目: {include_template}")
    
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
        
        # 如果需要获取详情，解析项目ID并查询详情
        if fetch_details:
            # 从输出中提取项目ID列表
            output = result.stdout
            response_marker = "响应:"
            
            if response_marker in output:
                json_start = output.index(response_marker) + len(response_marker)
                json_content = output[json_start:].strip()
                
                try:
                    # 解析 JSON - 这是 API 的原始响应
                    api_response = json.loads(json_content)
                    
                    # 提取项目ID列表
                    project_ids = []
                    if api_response.get("code") == 200 and "result" in api_response:
                        if api_response["result"]:
                            project_ids = api_response["result"]
                    
                    # 如果有项目ID，查询详情
                    if project_ids:
                        print(f"\n正在获取 {len(project_ids)} 个项目的详细信息...")
                        project_details = query_project_details(project_ids)
                        
                        if project_details:
                            print("\n" + "="*50)
                            print(f"✅ 项目详情获取成功！")
                            print("="*50)
                            print(json.dumps(project_details, ensure_ascii=False, indent=2))
                        else:
                            print("\n⚠️  获取项目详情失败")
                    
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
    include_template = False
    fetch_details = True
    
    # 如果没有参数或只有 --help，显示帮助信息
    if len(sys.argv) == 1:
        query_projects(tql, page_size, page_token, include_template, fetch_details)
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
        elif arg == "--include-template":
            include_template = True
            i += 1
        elif arg == "--no-details":
            fetch_details = False
            i += 1
        elif arg == "--help":
            print("用法: uv run scripts/query-projects.py [选项]")
            print("\n选项:")
            print("  --tql <TQL>              项目查询语言（可选）")
            print("  --page-size <大小>      每页大小（可选）")
            print("  --page-token <令牌>     分页令牌（可选）")
            print("  --include-template      包含模板项目（默认不包含）")
            print("  --no-details            不自动获取项目详情（默认会自动获取）")
            print("  --help                  显示此帮助信息")
            print("\n说明:")
            print("  - 默认情况下会自动排除模板项目（isTemplate = false）")
            print("  - 如果需要查询模板项目，请使用 --include-template 参数")
            print("  - TQL 中如果已经指定了 isTemplate 条件，则以 TQL 为准")
            print("\n项目 TQL 查询语法:")
            print("  筛选字段:")
            print("    - creatorId: 创建者ID")
            print("    - involveMembers: 项目成员ID")
            print("    - created: 创建时间")
            print("    - updated: 更新时间")
            print("    - visibility: 可见性（project/organization/org）")
            print("    - isArchived: 是否在回收站")
            print("    - isSuspended: 是否已归档")
            print("    - isTemplate: 是否是模板项目")
            print("    - text: 项目名称或简介")
            print("    - nameText: 项目名称")
            print("    - description: 项目简介")
            print("")
            print("  操作符:")
            print("    - =, !=: 等于、不等于")
            print("    - >, >=, <, <=: 大于、大于等于、小于、小于等于")
            print("    - ~: 模糊匹配")
            print("    - IN, NOT IN: 在列表中、不在列表中")
            print("    - AND, OR: 逻辑与、逻辑或")
            print("")
            print("  时间函数:")
            print("    - startOf(d): 今天开始")
            print("    - endOf(d): 今天结束")
            print("    - startOf(w): 本周开始")
            print("    - endOf(w): 本周结束")
            print("    - startOf(M): 本月开始")
            print("    - endOf(M): 本月结束")
            print("    - 支持偏移: startOf(d, -7d) 表示 7 天前")
            print("")
            print("  排序:")
            print("    - ORDER BY created ASC/DESC: 按创建时间升序/降序")
            print("    - ORDER BY updated ASC/DESC: 按更新时间升序/降序")
            print("\n示例:")
            print("  # 查询所有项目（自动获取详情，默认排除模板）")
            print("  uv run scripts/query-projects.py")
            print("")
            print("  # 查询包含'测试'的项目")
            print('  uv run scripts/query-projects.py --tql "nameText ~ \'测试\'"')
            print("")
            print("  # 查询今天更新的项目")
            print('  uv run scripts/query-projects.py --tql "updated <= endOf(d) AND updated >= startOf(d)"')
            print("")
            print("  # 查询过去7天创建的项目，按更新时间降序")
            print('  uv run scripts/query-projects.py --tql "created <= endOf(d, -1d) AND created >= startOf(d, -7d) ORDER BY updated DESC"')
            print("")
            print("  # 查询已归档的项目")
            print('  uv run scripts/query-projects.py --tql "isSuspended = true"')
            print("")
            print("  # 查询在回收站的项目")
            print('  uv run scripts/query-projects.py --tql "isArchived = true"')
            print("")
            print("  # 查询我创建的项目")
            print('  uv run scripts/query-projects.py --tql "creatorId = me()"')
            print("")
            print("  # 查询我参与的项目")
            print('  uv run scripts/query-projects.py --tql "involveMembers = me()"')
            print("")
            print("  # 设置每页大小")
            print("  uv run scripts/query-projects.py --page-size 20")
            print("")
            print("  # 包含模板项目")
            print("  uv run scripts/query-projects.py --include-template")
            print("")
            print("  # 只查询项目ID，不获取详情")
            print("  uv run scripts/query-projects.py --no-details")
            print("")
            print("  # 使用分页令牌")
            print('  uv run scripts/query-projects.py --page-token "xxx"')
            print("")
            print("  # 组合使用")
            print('  uv run scripts/query-projects.py --tql "nameText ~ \'开发\'" --page-size 20')
            sys.exit(0)
        else:
            print(f"❌ 错误: 未知参数 {arg}")
            sys.exit(1)
    
    # 执行查询
    success = query_projects(tql, page_size, page_token, include_template, fetch_details)
    
    # 根据结果退出
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
