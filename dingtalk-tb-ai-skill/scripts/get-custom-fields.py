#!/usr/bin/env python3
"""
Teambition 获取自定义字段脚本
调用 /v3/project/{projectId}/customfield/search 接口获取项目的自定义字段配置
"""

import subprocess
import sys
import json
from typing import Optional, List, Dict, Any

def get_custom_fields(project_id: str, cf_ids: Optional[str] = None, 
                      sfc_id: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
    """
    获取项目的自定义字段配置
    
    Args:
        project_id: 项目 ID（必需）
        cf_ids: 自定义字段 ID 列表，逗号分隔（可选）
        sfc_id: 任务类型 ID，用于过滤该类型相关的字段（可选）
        
    Returns:
        自定义字段列表，失败返回 None
    """
    # 构建查询参数
    query_params = []
    if cf_ids:
        query_params.append(f"cfIds={cf_ids}")
    if sfc_id:
        query_params.append(f"sfcId={sfc_id}")
    
    query_string = f"?{'&'.join(query_params)}" if query_params else ""
    
    # API 路径
    api_path = f"v3/project/{project_id}/customfield/search{query_string}"
    
    print(f"正在获取自定义字段配置...")
    print(f"  项目 ID: {project_id}")
    if cf_ids:
        print(f"  字段 ID: {cf_ids}")
    if sfc_id:
        print(f"  任务类型 ID: {sfc_id}")
    
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
                        custom_fields = api_response["result"]
                        
                        # 检查是否为空
                        if not custom_fields:
                            print("\n" + "="*50)
                            print("⚠️  未找到任何自定义字段")
                            print("="*50)
                            return []
                        
                        # 输出格式化的结果
                        print("\n" + "="*50)
                        print(f"✅ 查询成功！共找到 {len(custom_fields)} 个自定义字段")
                        print("="*50)
                        
                        for idx, field in enumerate(custom_fields, 1):
                            print(f"\n【字段 {idx}】")
                            print(f"  ID: {field.get('id')}")
                            print(f"  名称: {field.get('name')}")
                            print(f"  类型: {field.get('type')}")
                            
                            # 显示子类型
                            if field.get('subtype'):
                                print(f"  子类型: {field.get('subtype')}")
                            
                            # 显示可选项（如果是单选或多选字段）
                            choices = field.get('choices', [])
                            if choices:
                                print(f"  可选项: {len(choices)} 个")
                                for choice in choices[:5]:  # 只显示前5个
                                    print(f"    - {choice.get('value')} (ID: {choice.get('id')})")
                                if len(choices) > 5:
                                    print(f"    ... 还有 {len(choices) - 5} 个选项")
                            
                            # 显示绑定信息
                            if field.get('boundToObjectId'):
                                print(f"  绑定对象 ID: {field.get('boundToObjectId')}")
                            if field.get('boundToObjectType'):
                                print(f"  绑定对象类型: {field.get('boundToObjectType')}")
                            
                            # 显示创建信息
                            if field.get('created'):
                                print(f"  创建时间: {field.get('created')}")
                        
                        print("\n完整信息:")
                        print(json.dumps(custom_fields, ensure_ascii=False, indent=2))
                        
                        return custom_fields
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
        print("用法: uv run scripts/get-custom-fields.py <项目ID> [选项]")
        print("\n参数:")
        print("  项目ID                   项目 ID（必需）")
        print("\n选项:")
        print("  --cf-ids <ID列表>       自定义字段 ID 列表，逗号分隔")
        print("  --sfc-id <ID>           任务类型 ID，用于过滤该类型相关的字段")
        print("  --help                  显示此帮助信息")
        print("\n说明:")
        print("  - 如果不指定任何选项，将返回项目的所有自定义字段")
        print("  - 使用 --cf-ids 可以批量查询指定的字段")
        print("  - 使用 --sfc-id 可以查询特定任务类型相关的字段")
        print("\n示例:")
        print("  # 获取项目所有自定义字段")
        print("  uv run scripts/get-custom-fields.py 67ec9b8c3c6130ac88605c3e")
        print("")
        print("  # 批量获取指定字段")
        print("  uv run scripts/get-custom-fields.py 67ec9b8c3c6130ac88605c3e \\")
        print("    --cf-ids '67ec9b8c3c6130ac88605c3f,67ec9b8c3c6130ac88605c40'")
        print("")
        print("  # 获取特定任务类型的字段")
        print("  uv run scripts/get-custom-fields.py 67ec9b8c3c6130ac88605c3e \\")
        print("    --sfc-id 67ec9b8c3c6130ac88605c3f")
        sys.exit(0)
    
    # 解析参数
    project_id = sys.argv[1]
    cf_ids = None
    sfc_id = None
    
    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg == "--cf-ids" and i + 1 < len(sys.argv):
            cf_ids = sys.argv[i + 1]
            i += 2
        elif arg == "--sfc-id" and i + 1 < len(sys.argv):
            sfc_id = sys.argv[i + 1]
            i += 2
        else:
            print(f"❌ 错误: 未知参数 {arg}")
            sys.exit(1)
    
    # 执行查询
    result = get_custom_fields(project_id, cf_ids, sfc_id)
    
    # 根据结果退出
    if result is not None:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
