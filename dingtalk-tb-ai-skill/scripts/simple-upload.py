#!/usr/bin/env python3
"""
简化版文件上传脚本
使用 HTTP 请求方式上传文件，避免使用 SDK
"""

import subprocess
import sys
import json
import os
import mimetypes
import requests
from typing import Optional, Dict, Any


def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    获取文件信息
    
    Args:
        file_path: 文件路径
        
    Returns:
        包含文件信息的字典
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    file_size = os.path.getsize(file_path)
    file_name = os.path.basename(file_path)
    file_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
    
    return {
        'file_path': file_path,
        'file_name': file_name,
        'file_size': file_size,
        'file_type': file_type
    }


def get_upload_token(scope: str, file_size: int, file_type: str, 
                     file_name: str, category: str) -> Optional[Dict[str, Any]]:
    """
    步骤 1：获取上传凭证
    
    Args:
        scope: 业务范围
        file_size: 文件大小
        file_type: 文件类型
        file_name: 文件名
        category: 文件类别
        
    Returns:
        上传凭证信息，包含 uploadUrl 和 token
    """
    try:
        payload = {
            "scope": scope,
            "fileSize": file_size,
            "fileType": file_type,
            "fileName": file_name,
            "category": category
        }
        
        payload_json = json.dumps(payload, ensure_ascii=False)
        
        print(f"📋 步骤 1：获取上传凭证")
        print(f"  Scope: {scope}")
        print(f"  文件名: {file_name}")
        print(f"  文件大小: {file_size} 字节 ({file_size / 1024 / 1024:.2f} MB)")
        print(f"  文件类型: {file_type}")
        print(f"  类别: {category}")
        
        result = subprocess.run(
            ["uv", "run", "scripts/call-user-api.py", "POST", "v3/awos/upload-token", payload_json],
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
                    
                    # 提取关键信息 - 数据在 result 字段中
                    result = api_response.get("result", {})
                    upload_url = result.get("uploadUrl")
                    file_token = result.get("token")
                    
                    if upload_url and file_token:
                        print(f"✅ 上传凭证获取成功")
                        return {
                            "uploadUrl": upload_url,
                            "token": file_token
                        }
                    else:
                        print(f"❌ 响应中缺少必要字段")
                        print(f"响应内容: {api_response}")
                        return None
                except json.JSONDecodeError as e:
                    print(f"❌ JSON 解析失败: {e}")
                    return None
        
        print("❌ 获取上传凭证失败")
        print(result.stdout)
        return None
    except Exception as e:
        print(f"❌ 发生异常: {str(e)}")
        return None


def upload_file_to_oss(file_path: str, upload_url: str, file_type: str) -> bool:
    """
    步骤 2：使用 HTTP PUT 请求上传文件到 OSS
    
    Args:
        file_path: 文件路径
        upload_url: 预签名 URL
        file_type: 文件类型
        
    Returns:
        是否上传成功
    """
    try:
        print(f"\n📤 步骤 2：上传文件到 OSS")
        print(f"  文件: {os.path.basename(file_path)}")
        print(f"  方式: HTTP PUT 请求")
        
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        # 使用 PUT 请求上传文件，预签名 URL 不需要额外的头信息
        response = requests.put(
            upload_url,
            data=file_data
        )
        
        if response.status_code in [200, 204]:
            print(f"✅ 文件上传成功")
            return True
        else:
            print(f"❌ 文件上传失败")
            print(f"  状态码: {response.status_code}")
            print(f"  响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 上传失败: {str(e)}")
        return False


def upload_file(file_path: str, scope: str, category: str) -> Optional[str]:
    """
    完整的文件上传流程
    
    Args:
        file_path: 文件路径
        scope: 业务范围
        category: 文件类别
        
    Returns:
        文件 Token，失败返回 None
    """
    try:
        print("\n" + "="*60)
        print("Teambition 文件上传（简化版）")
        print("="*60 + "\n")
        
        # 获取文件信息
        file_info = get_file_info(file_path)
        
        # 步骤 1：获取上传凭证
        upload_token_info = get_upload_token(
            scope=scope,
            file_size=file_info['file_size'],
            file_type=file_info['file_type'],
            file_name=file_info['file_name'],
            category=category
        )
        
        if not upload_token_info:
            return None
        
        upload_url = upload_token_info.get('uploadUrl')
        file_token = upload_token_info.get('token')
        
        if not upload_url or not file_token:
            print("❌ 错误: 未获取到上传 URL 或文件 Token")
            return None
        
        # 步骤 2：上传文件到 OSS
        success = upload_file_to_oss(
            file_path=file_path,
            upload_url=upload_url,
            file_type=file_info['file_type']
        )
        
        if not success:
            return None
        
        # 步骤 3：返回文件 Token
        print(f"\n🎉 步骤 3：上传完成")
        print(f"  文件 Token: {file_token}")
        
        print("\n" + "="*60)
        print("✅ 上传成功！")
        print("="*60)
        print(f"\n📌 文件 Token: {file_token}")
        print("\n💡 提示: 可以在任务评论、自定义字段等场景使用此 Token")
        
        return file_token
            
    except FileNotFoundError as e:
        print(f"❌ {str(e)}")
        return None
    except Exception as e:
        print(f"❌ 发生异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """主函数"""
    if "--help" in sys.argv or len(sys.argv) < 2:
        print("=" * 60)
        print("Teambition 文件上传脚本（简化版）")
        print("=" * 60)
        print("\n用法: uv run scripts/simple-upload.py [选项]")
        print("\n必需参数:")
        print("  --file-path <路径>      文件路径（必需）")
        print("  --scope <范围>          业务范围，格式: ${object}:${id}（必需）")
        print("  --category <类别>       文件类别（必需）")
        print("\n可选参数:")
        print("  --help                  显示此帮助信息")
        print("\n" + "=" * 60)
        print("Scope 格式说明")
        print("=" * 60)
        print("  任务: task:{taskId}")
        print("    示例: task:628cd5bff0396403950f3fdb")
        print("\n  项目: project:{projectId}")
        print("    示例: project:628cd5bff0396403950f3fdb")
        print("\n  富文本: rich-text:{id}")
        print("    示例: rich-text:628cd5bff0396403950f3fdb")
        print("\n" + "=" * 60)
        print("Category 类别说明")
        print("=" * 60)
        print("  attachment             普通附件（最常用，推荐）")
        print("  rich-text              富文本内容")
        print("  rich-text-attachment   富文本附件")
        print("  work                   工作文件")
        print("\n" + "=" * 60)
        print("使用示例")
        print("=" * 60)
        print("\n1. 上传图片到任务:")
        print("   uv run scripts/simple-upload.py \\")
        print("     --file-path '/path/to/image.jpg' \\")
        print("     --scope 'task:69a252ad3e86c360f083e06c' \\")
        print("     --category 'attachment'")
        print("\n2. 上传 PDF 文档到项目:")
        print("   uv run scripts/simple-upload.py \\")
        print("     --file-path '/path/to/document.pdf' \\")
        print("     --scope 'project:69a03cd9cd778ff7d8974858' \\")
        print("     --category 'attachment'")
        print("\n3. 上传富文本图片:")
        print("   uv run scripts/simple-upload.py \\")
        print("     --file-path '/path/to/diagram.png' \\")
        print("     --scope 'task:69a252ad3e86c360f083e06c' \\")
        print("     --category 'rich-text'")
        print("\n" + "=" * 60)
        print("特点")
        print("=" * 60)
        print("  ✅ 使用 HTTP PUT 请求上传，无需 SDK")
        print("  ✅ 自动检测文件类型")
        print("  ✅ 清晰的步骤提示")
        print("  ✅ 返回文件 Token 供后续使用")
        print("\n详细文档: docs/file-upload.md")
        print("=" * 60)
        sys.exit(0)
    
    # 解析参数
    file_path = None
    scope = None
    category = None
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg == "--file-path" and i + 1 < len(sys.argv):
            file_path = sys.argv[i + 1]
            i += 2
        elif arg == "--scope" and i + 1 < len(sys.argv):
            scope = sys.argv[i + 1]
            i += 2
        elif arg == "--category" and i + 1 < len(sys.argv):
            category = sys.argv[i + 1]
            i += 2
        else:
            print(f"❌ 错误: 未知参数 {arg}")
            print("使用 --help 查看帮助信息")
            sys.exit(1)
    
    # 验证必需参数
    if not file_path:
        print("❌ 错误: 缺少必需参数 --file-path")
        print("使用 --help 查看帮助信息")
        sys.exit(1)
    
    if not scope:
        print("❌ 错误: 缺少必需参数 --scope")
        print("使用 --help 查看帮助信息")
        sys.exit(1)
    
    if not category:
        print("❌ 错误: 缺少必需参数 --category")
        print("使用 --help 查看帮助信息")
        sys.exit(1)
    
    # 验证 category
    valid_categories = ['rich-text', 'rich-text-attachment', 'attachment', 'work']
    if category not in valid_categories:
        print(f"❌ 错误: 无效的 category '{category}'")
        print(f"有效选项: {', '.join(valid_categories)}")
        sys.exit(1)
    
    # 上传文件
    file_token = upload_file(file_path, scope, category)
    
    if file_token:
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("❌ 上传失败")
        print("="*60)
        sys.exit(1)


if __name__ == "__main__":
    main()
