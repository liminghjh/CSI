from langchain.agents import create_agent
from CSI.config import tools_config

#创建安全评估Agent,默认使用配置文件中的工具
#需要传入参数，模型，工具，系统提示语
def create_security_agent(Aimodel=None, AItools=None, system_prompt=None):
    security_agent = create_agent(
        model=Aimodel,
        tools=AItools if AItools else tools_config,
        system_prompt=system_prompt 
        )
    return security_agent