#!/usr/bin/env python3
"""
Teambition 获取当前用户信息脚本
调用 /users/me 接口获取当前用户的基本信息
"""

import subprocess
import sys
import json
from typing import Optional, Dict, Any

def get_current_user() -> Optional[Dict[str, Any]]:
    """
    获取当前用户信息
    
    Returns:
        用户信息字典，包含 userId 和 name，失败返回 None
    """
    # API 路径
    api_path = "users/me"
    
    print(f"正在获取当前用户信息...")
    
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
                    
                    # API 响应格式: {"requestId": "...", "result": {...}, "traceId": "..."}
                    if "result" not in api_response:
                        print("\n" + "="*50)
                        print("❌ API 响应格式异常，缺少 result 字段")
                        print("="*50)
                        print(json.dumps(api_response, ensure_ascii=False, indent=2))
                        return None
                    
                    user_info = api_response["result"]
                    
                    # 提取关键信息
                    user_data = {
                        "userId": user_info.get("userId"),
                        "name": user_info.get("name"),
                        "email": user_info.get("email"),
                        "phone": user_info.get("phone"),
                        "role": user_info.get("role"),
                        "isDisabled": user_info.get("isDisabled"),
                        "employeeNumber": user_info.get("employeeNumber")
                    }
                    
                    # 输出格式化的结果
                    print("\n" + "="*50)
                    print(f"✅ 获取用户信息成功！")
                    print("="*50)
                    print(f"用户 ID: {user_data['userId']}")
                    print(f"用户名称: {user_data['name']}")
                    if user_data['email']:
                        print(f"邮箱: {user_data['email']}")
                    if user_data['phone']:
                        print(f"电话: {user_data['phone']}")
                    if user_data['employeeNumber']:
                        print(f"工号: {user_data['employeeNumber']}")
                    
                    role_map = {
                        -1: "外部成员",
                        0: "成员",
                        1: "管理员",
                        2: "拥有者"
                    }
                    role_name = role_map.get(user_data['role'], "未知")
                    print(f"角色: {role_name}")
                    print(f"账号状态: {'停用' if user_data['isDisabled'] == 1 else '启用'}")
                    
                    print("\n完整信息:")
                    print(json.dumps(user_data, ensure_ascii=False, indent=2))
                    
                    return user_data
                        
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
    # 如果有 --help 参数，显示帮助信息
    if "--help" in sys.argv:
        print("用法: uv run scripts/get-current-user.py")
        print("\n说明:")
        print("  获取当前用户在企业中的基本成员信息")
        print("  该接口只适用于 User Token 认证")
        print("\n返回信息:")
        print("  - userId: 用户 ID")
        print("  - name: 用户名称")
        print("  - email: 电子邮箱")
        print("  - phone: 联系电话")
        print("  - role: 成员角色（-1: 外部成员, 0: 成员, 1: 管理员, 2: 拥有者）")
        print("  - isDisabled: 账号状态（0: 启用, 1: 停用）")
        print("  - employeeNumber: 员工工号")
        print("\n示例:")
        print("  # 获取当前用户信息")
        print("  uv run scripts/get-current-user.py")
        sys.exit(0)
    
    # 执行查询
    user_info = get_current_user()
    
    # 根据结果退出
    if user_info:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
