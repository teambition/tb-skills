#!/usr/bin/env python3
"""
Teambition 获取项目任务类型脚本
调用 /v3/project/{projectId}/scenariofieldconfig/search 接口获取项目的任务类型配置
"""

import subprocess
import sys
import json
from typing import Optional, List, Dict, Any

def get_scenario_types(project_id: str, scenario_id: Optional[str] = None, 
                       scenario_name: Optional[str] = None,
                       q: Optional[str] = None,
                       return_default: bool = False) -> Optional[List[Dict[str, Any]]]:
    """
    获取项目的任务类型列表
    
    Args:
        project_id: 项目 ID（必需）
        scenario_id: 任务类型 ID（可选）
        scenario_name: 任务类型名称（可选）
        q: 根据名称搜索任务类型（可选，支持模糊匹配）
        return_default: 是否只返回默认类型（第一个）
        
    Returns:
        任务类型列表或单个任务类型，失败返回 None
    """
    # 构建查询参数
    query_params = []
    if scenario_id:
        query_params.append(f"sfcIds={scenario_id}")
    if q:
        query_params.append(f"q={q}")
    
    query_string = f"?{'&'.join(query_params)}" if query_params else ""
    
    # API 路径
    api_path = f"v3/project/{project_id}/scenariofieldconfig/search{query_string}"
    
    print(f"正在获取项目任务类型...")
    print(f"  项目 ID: {project_id}")
    if scenario_id:
        print(f"  任务类型 ID: {scenario_id}")
    if scenario_name:
        print(f"  任务类型名称: {scenario_name}")
    if q:
        print(f"  搜索关键词: {q}")
    
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
                        scenario_types = api_response["result"]
                        
                        # 检查是否为空
                        if not scenario_types:
                            print("\n" + "="*50)
                            print("⚠️  未找到任何任务类型")
                            print("="*50)
                            return []
                        
                        # 如果指定了任务类型名称，进行过滤
                        if scenario_name:
                            filtered = [st for st in scenario_types if st.get("name") == scenario_name]
                            if not filtered:
                                print("\n" + "="*50)
                                print(f"⚠️  未找到名称为 '{scenario_name}' 的任务类型")
                                print("="*50)
                                print("可用的任务类型:")
                                for st in scenario_types:
                                    print(f"  - {st.get('name')} (ID: {st.get('id')})")
                                return None
                            scenario_types = filtered
                        
                        # 如果只返回默认类型（第一个）
                        if return_default and scenario_types:
                            scenario_types = [scenario_types[0]]
                        
                        # 输出格式化的结果
                        print("\n" + "="*50)
                        print(f"✅ 查询成功！共找到 {len(scenario_types)} 个任务类型")
                        print("="*50)
                        
                        for idx, st in enumerate(scenario_types, 1):
                            print(f"\n【任务类型 {idx}】")
                            print(f"  ID: {st.get('id')}")
                            print(f"  名称: {st.get('name')}")
                            print(f"  图标: {st.get('icon', 'N/A')}")
                            print(f"  类型: {st.get('type', 'N/A')}")
                            
                            # 显示字段配置
                            scenariofields = st.get('scenariofields', [])
                            if scenariofields:
                                print(f"  字段配置: {len(scenariofields)} 个字段")
                                required_fields = [f for f in scenariofields if f.get('required')]
                                if required_fields:
                                    print(f"  必填字段: {len(required_fields)} 个")
                                    for field in required_fields:
                                        print(f"    - {field.get('fieldType')} (字段ID: {field.get('customfieldId')})")
                        
                        print("\n完整信息:")
                        print(json.dumps(scenario_types, ensure_ascii=False, indent=2))
                        
                        return scenario_types
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
        print("用法: uv run scripts/get-scenario-types.py <项目ID> [选项]")
        print("\n参数:")
        print("  项目ID                   项目 ID（必需）")
        print("\n选项:")
        print("  --scenario-id <ID>      任务类型 ID")
        print("  --scenario-name <名称>  任务类型名称（精确匹配）")
        print("  --q <关键词>            根据名称搜索（支持模糊匹配）")
        print("  --default               只返回默认类型（第一个）")
        print("  --help                  显示此帮助信息")
        print("\n示例:")
        print("  # 获取项目所有任务类型")
        print("  uv run scripts/get-scenario-types.py 67ec9b8c3c6130ac88605c3e")
        print("")
        print("  # 获取默认任务类型（第一个）")
        print("  uv run scripts/get-scenario-types.py 67ec9b8c3c6130ac88605c3e --default")
        print("")
        print("  # 根据名称搜索任务类型（模糊匹配）")
        print("  uv run scripts/get-scenario-types.py 67ec9b8c3c6130ac88605c3e --q '需求'")
        print("  uv run scripts/get-scenario-types.py 67ec9b8c3c6130ac88605c3e --q '缺陷'")
        print("")
        print("  # 获取指定 ID 的任务类型")
        print("  uv run scripts/get-scenario-types.py 67ec9b8c3c6130ac88605c3e --scenario-id 67ec9b8c3c6130ac88605c3f")
        print("")
        print("  # 获取指定名称的任务类型（精确匹配）")
        print("  uv run scripts/get-scenario-types.py 67ec9b8c3c6130ac88605c3e --scenario-name '需求'")
        sys.exit(0)
    
    # 解析参数
    project_id = sys.argv[1]
    scenario_id = None
    scenario_name = None
    q = None
    return_default = False
    
    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg == "--scenario-id" and i + 1 < len(sys.argv):
            scenario_id = sys.argv[i + 1]
            i += 2
        elif arg == "--scenario-name" and i + 1 < len(sys.argv):
            scenario_name = sys.argv[i + 1]
            i += 2
        elif arg == "--q" and i + 1 < len(sys.argv):
            q = sys.argv[i + 1]
            i += 2
        elif arg == "--default":
            return_default = True
            i += 1
        else:
            print(f"❌ 错误: 未知参数 {arg}")
            sys.exit(1)
    
    # 执行查询
    result = get_scenario_types(project_id, scenario_id, scenario_name, q, return_default)
    
    # 根据结果退出
    if result is not None:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
