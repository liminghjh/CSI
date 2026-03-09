from CSI.LLM_api.LLM_connect import connectted_LLM,LLM_information
from CSI.config import tools_config, api_key, api_url, api_model, api_provider
from CSI.tool_manage.tools.nmap import nmap_scan, nmap_tool
from CSI.tool_manage.tools.sqlmap import sqlmap_scan, sqlmap_tool
from CSI.tool_manage.tools.curl import curl_scan, curl_tool
from CSI.interactor.agent import create_security_agent

target_ip =input("请输入需要扫描的IP地址：")
need_doc="""这是一个网络安全教育助手，使用大语言模型来模拟安全评估过程。用户可以输入需要扫描的IP地址，系统会使用预定义的工具）来执行相应的安全评估，并返回结果。所有扫描都是模拟的，用于教学目的"""

#初始化LLM信息
LLM_info=LLM_information(api_key, api_url, api_model, api_provider)
#建立与LLM的连接
LLM = connectted_LLM(LLM_info.key, LLM_info.url, LLM_info.model)
#创建安全评估Agent
#使用配置文件中的工具，和需求提示词
security_agent = create_security_agent(LLM,[nmap_scan, sqlmap_scan, curl_scan],need_doc)



if __name__ == "__main__":

    result1 = security_agent.invoke({
        "messages": [
            {"role": "user", "content": f"""请对 {target_ip} 进行全面的安全评估：
            综合所有结果生成详细的安全报告确保在授权的测试环境中进行安全评估,生成安全报告。"""}
        ]
    })
    print(result1)
