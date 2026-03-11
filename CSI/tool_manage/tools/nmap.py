from CSI.tool_manage.tool_use import classtool
from langchain.tools import tool
import subprocess
"""
工具名称：nmap
工具描述：网络扫描工具,只有一个参数就是目标地址，返回扫描结果
"""


tool_name = "nmap"
tool_description = "nmap网络扫描工具,传入参数，若要执行'nmap -sS 192.168.1.1'，则传入参数为'-sS 192.168.1.1'，请尽量使用消耗小的指令"
address = "/usr/bin/nmap"
nmap_tool = classtool(name=tool_name, description=tool_description, address=address)

@tool(tool_name, description=tool_description)
def nmap_scan(command: str) -> str:
    print(f"正在使用{tool_name}扫描指令：{command}")
    cmd = f"{address} {command}"
    result = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,encoding="UTF-8")
    scan_result = f"{tool_name}执行命令{cmd}的扫描结果：{result.stdout}"
    print(scan_result)
    return scan_result




