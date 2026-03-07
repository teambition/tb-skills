#!/usr/bin/env python3
"""
Teambition 泛化 API 调用工具
使用 User Token 认证，支持 GET、POST、DELETE、PUT 等 HTTP 方法
"""

import requests
import json
import sys
import os
from typing import Dict, Any, Optional

# ================= 配置信息 =================
# 从环境变量读取 User Token
USER_TOKEN = os.environ.get("TB_USER_TOKEN")
CONFIG_FILE = "user-token.json"

# 默认 API 基础 URL
DEFAULT_API_BASE_URL = "https://open.teambition.com/api"
# 从环境变量读取 API 基础 URL（可选）
API_BASE_URL = os.environ.get("TB_API_BASE_URL") or DEFAULT_API_BASE_URL
# ===========================================

def load_user_token() -> Optional[str]:
    """
    加载 User Token，优先从环境变量读取，其次从配置文件读取
    
    Returns:
        User Token 字符串，如果无法获取则返回 None
    """
    # 优先使用环境变量
    if USER_TOKEN:
        return USER_TOKEN
    
    # 从配置文件读取
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('userToken')
        except Exception as e:
            print(f"❌ 读取配置文件失败: {e}")
    
    return None

def get_headers() -> Dict[str, str]:
    """
    获取 API 请求头
    
    Returns:
        包含认证信息的请求头字典
    """
    token = load_user_token()
    if not token:
        print("❌ 错误: 无法获取 User Token")
        print("请设置环境变量 TB_USER_TOKEN 或创建 user-token.json 配置文件")
        sys.exit(1)
    
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def call_user_api(method: str, url: str, body: Optional[Dict[str, Any]] = None,
             params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    泛化 API 调用方法
    
    Args:
        method: HTTP 方法（GET、POST、DELETE、PUT）
        url: API 请求 URL（可以是完整 URL 或相对路径）
        body: 请求体（可选），用于 POST、PUT 等方法
        params: URL 查询参数（可选），用于 GET 方法
    
    Returns:
        dict: 包含响应结果的字典
    """
    try:
        headers = get_headers()
        method = method.upper()
        
        # 如果 URL 不是完整的 URL（不以 http:// 或 https:// 开头），则拼接默认的 API 基础 URL
        if not url.startswith("http://") and not url.startswith("https://"):
            full_url = f"{API_BASE_URL}/{url.lstrip('/')}"
        else:
            full_url = url
        
        print(f"正在调用 API...")
        print(f"  方法: {method}")
        print(f"  URL: {full_url}")
        if params:
            print(f"  查询参数: {json.dumps(params, ensure_ascii=False)}")
        if body:
            print(f"  请求体: {json.dumps(body, ensure_ascii=False)}")
        
        # 根据不同的 HTTP 方法发送请求
        if method == "GET":
            response = requests.get(full_url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(full_url, headers=headers, data=json.dumps(body) if body else None, params=params)
        elif method == "PUT":
            response = requests.put(full_url, headers=headers, data=json.dumps(body) if body else None, params=params)
        elif method == "DELETE":
            response = requests.delete(full_url, headers=headers, params=params)
        else:
            return {
                "success": False,
                "message": f"不支持的 HTTP 方法: {method}"
            }
        
        # 处理响应
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ API 调用成功！")
                print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
                return {
                    "success": True,
                    "data": result,
                    "status_code": response.status_code
                }
            except json.JSONDecodeError:
                # 响应不是 JSON 格式
                print(f"✅ API 调用成功！")
                print(f"响应: {response.text}")
                return {
                    "success": True,
                    "data": response.text,
                    "status_code": response.status_code
                }
        else:
            error_msg = f"API 调用失败，状态码: {response.status_code}"
            try:
                error_detail = response.json()
                error_msg += f", 错误信息: {json.dumps(error_detail, ensure_ascii=False)}"
            except:
                error_msg += f", 响应内容: {response.text}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "message": error_msg,
                "status_code": response.status_code
            }
            
    except requests.exceptions.RequestException as e:
        error_msg = f"网络请求异常: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "success": False,
            "message": error_msg
        }
    except Exception as e:
        error_msg = f"发生异常: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "success": False,
            "message": error_msg
        }

def main():
    """主函数 - 命令行入口"""
    if len(sys.argv) < 3:
        print("用法: uv run call-user-api.py <方法> <URL> [请求体]")
        print("\n参数:")
        print("  方法: GET、POST、PUT、DELETE（不区分大小写）")
        print("  URL: API 请求地址（完整 URL 或相对路径）")
        print("  请求体: JSON 格式的请求体（可选），用于 POST、PUT 方法")
        print("\n说明:")
        print("  - URL 可以是完整 URL（如 https://open.teambition.com/api/v3/project/query）")
        print("  - 也可以是相对路径（如 v3/project/query），会自动拼接默认 API 基础 URL")
        print(f"  - 默认 API 基础 URL: {API_BASE_URL}")
        print("  - 可通过环境变量 TB_API_BASE_URL 自定义 API 基础 URL")
        print("\n示例:")
        print("  # GET 请求 - 使用完整 URL")
        print("  uv run call-user-api.py GET https://open.teambition.com/api/v3/project/query")
        print("")
        print("  # GET 请求 - 使用相对路径（推荐）")
        print("  uv run call-user-api.py GET v3/project/query")
        print("")
        print("  # GET 请求带参数")
        print("  uv run call-user-api.py GET 'v3/project/searchTasks?projectId=xxx'")
        print("")
        print("  # POST 请求")
        print('  uv run call-user-api.py POST v3/task/create \'{"projectId":"xxx","content":"任务标题"}\'')
        print("")
        print("  # PUT 请求")
        print('  uv run call-user-api.py PUT v3/task/xxx/status \'{"status":"done"}\'')
        print("")
        print("  # DELETE 请求")
        print("  uv run call-user-api.py DELETE v3/task/xxx")
        sys.exit(1)
    
    method = sys.argv[1]
    url = sys.argv[2]
    body = None
    
    # 解析请求体（如果有）
    if len(sys.argv) > 3:
        try:
            body = json.loads(sys.argv[3])
        except json.JSONDecodeError as e:
            print(f"❌ 请求体 JSON 解析失败: {e}")
            print("请确保请求体是有效的 JSON 格式")
            sys.exit(1)
    
    # 调用 API
    result = call_user_api(method, url, body)
    
    # 根据结果退出
    if result.get("success"):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()