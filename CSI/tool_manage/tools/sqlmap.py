from CSI.tool_manage.tool_use import classtool
from langchain.tools import tool

"""
工具名称：sqlmap
工具描述：网络扫描工具,只有一个参数就是目标地址，返回扫描结果
"""


tool_name = "sqlmap"
tool_description = "网络扫描工具,只有一个参数就是目标地址，返回扫描结果"
address = "XXXX"

@tool(tool_name, description=tool_description)
def sqlmap_scan(target: str) -> str:
    print(f"正在使用{tool_name}扫描目标：{target}")
    # 模拟扫描结果
    scan_result = f"sqlmap扫描结果：{target}存在SQL注入漏洞，漏洞类型为Boolean-based blind，风险等级为高"
    print(f"{tool_name}扫描完成，结果：{scan_result}")
    return scan_result

sqlmap_tool = classtool(name=tool_name, description=tool_description, address=address)






