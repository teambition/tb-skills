#!/usr/bin/env python3
"""
Teambition 查询企业成员信息脚本
调用 /v3/member/query 接口查询企业成员信息
"""

import subprocess
import sys
import json
from typing import Optional, List, Dict, Any

def query_members(user_ids: Optional[str] = None, 
                 query: Optional[str] = None,
                 page_size: Optional[int] = None,
                 page_token: Optional[str] = None) -> bool:
    """
    查询企业成员信息
    
    Args:
        user_ids: 用户ID集合，逗号分隔（可选）
        query: 搜索关键字（可选）
        page_size: 分页数量（可选）
        page_token: 分页标（可选）
    
    Returns:
        bool: 查询是否成功
    """
    # 构建查询参数
    params = {}
    if user_ids:
        params["userIds"] = user_ids
    if query:
        params["q"] = query
    if page_size:
        params["pageSize"] = page_size
    if page_token:
        params["pageToken"] = page_token
    
    # 构建查询字符串
    query_string = ""
    if params:
        query_string = "?" + "&".join([f"{k}={v}" for k, v in params.items()])
    
    # API 路径
    api_path = f"v3/member/query{query_string}"
    
    print(f"正在查询企业成员信息...")
    if user_ids:
        print(f"  用户ID: {user_ids}")
    if query:
        print(f"  搜索关键字: {query}")
    if page_size:
        print(f"  每页大小: {page_size}")
    if page_token:
        print(f"  分页令牌: {page_token}")
    
    # 调用 call-user-api 脚本
    try:
        result = subprocess.run(
            ["uv", "run", "scripts/call-user-api.py", "POST", api_path],
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
                    
                    # API 响应格式: {"result": [...], "nextPageToken": "..."}
                    if "result" in api_response:
                        members = api_response["result"]
                        next_page_token = api_response.get("nextPageToken")

                        # 检查是否为空
                        if not members:
                            print("\n" + "="*50)
                            print("⚠️  未找到任何成员")
                            print("="*50)
                            return True
                        
                        # 提取简化的成员信息
                        simple_members = []
                        for member in members:
                            simple_member = {
                                "userId": member.get("userId"),
                                "name": member.get("name"),
                                "role": member.get("role"),
                                "isDisabled": member.get("isDisabled"),
                                "email": member.get("profile", {}).get("email"),
                                "phone": member.get("profile", {}).get("phone"),
                                "employeeNumber": member.get("profile", {}).get("employeeNumber"),
                                "position": member.get("profile", {}).get("position")
                            }
                            simple_members.append(simple_member)
                        
                        # 输出格式化的结果
                        print("\n" + "="*50)
                        print(f"✅ 查询成功！共找到 {len(simple_members)} 个成员")
                        print("="*50)
                        
                        # 输出成员列表
                        for i, member in enumerate(simple_members, 1):
                            role_map = {
                                -1: "外部成员",
                                0: "成员",
                                1: "管理员",
                                2: "拥有者"
                            }
                            role_name = role_map.get(member['role'], "未知")
                            status = "停用" if member['isDisabled'] else "启用"
                            
                            print(f"\n{i}. {member['name']} ({member['userId']})")
                            print(f"   角色: {role_name}")
                            print(f"   状态: {status}")
                            if member['email']:
                                print(f"   邮箱: {member['email']}")
                            if member['phone']:
                                print(f"   电话: {member['phone']}")
                            if member['employeeNumber']:
                                print(f"   工号: {member['employeeNumber']}")
                            if member['position']:
                                print(f"   职位: {member['position']}")
                        
                        # 输出分页信息
                        if next_page_token:
                            print(f"\n下一页令牌: {next_page_token}")
                        
                        # 输出完整 JSON
                        print("\n完整信息:")
                        print(json.dumps(simple_members, ensure_ascii=False, indent=2))
                        
                        return True
                    else:
                        # API 响应中没有 result 字段
                        print("\n" + "="*50)
                        print("❌ API 响应格式异常，缺少 result 字段")
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
    # 如果有 --help 参数，显示帮助信息
    if "--help" in sys.argv or len(sys.argv) < 2:
        print("用法: uv run scripts/query-members.py [选项]")
        print("\n选项:")
        print("  --user-ids <ID集合>     用户ID集合，逗号分隔（可选）")
        print("  --query <关键字>        搜索关键字（可选）")
        print("  --page-size <大小>      分页数量（可选）")
        print("  --page-token <令牌>     分页令牌（可选）")
        print("  --help                  显示此帮助信息")
        print("\n说明:")
        print("  - 如果提供 userIds，则忽略其他查询条件")
        print("  - 搜索关键字支持匹配：工号、姓名、英文名、邮箱、手机号")
        print("  - 至少需要提供 --user-ids 或 --query 参数之一")
        print("\n示例:")
        print("  # 根据用户ID查询")
        print("  uv run scripts/query-members.py --user-ids 696f2c084a459842b42b035b")
        print("")
        print("  # 根据多个用户ID查询")
        print("  uv run scripts/query-members.py --user-ids 696f2c084a459842b42b035b,696f2c084a459842b42b035c")
        print("")
        print("  # 根据关键字搜索")
        print("  uv run scripts/query-members.py --query 张三")
        print("")
        print("  # 搜索并设置分页")
        print("  uv run scripts/query-members.py --query 李 --page-size 10")
        print("")
        print("  # 使用分页令牌获取下一页")
        print('  uv run scripts/query-members.py --query 李 --page-token "xxx"')
        sys.exit(0)
    
    # 解析参数
    user_ids = None
    query = None
    page_size = None
    page_token = None
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg == "--user-ids" and i + 1 < len(sys.argv):
            user_ids = sys.argv[i + 1]
            i += 2
        elif arg == "--query" and i + 1 < len(sys.argv):
            query = sys.argv[i + 1]
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
        else:
            print(f"❌ 错误: 未知参数 {arg}")
            sys.exit(1)
    
    # 验证参数
    if not user_ids and not query:
        print("❌ 错误: 至少需要提供 --user-ids 或 --query 参数之一")
        sys.exit(1)
    
    # 执行查询
    success = query_members(user_ids, query, page_size, page_token)
    
    # 根据结果退出
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
