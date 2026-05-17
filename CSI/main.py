from CSI.LLM_api.LLM_connect import connectted_LLM,create_security_agent,queryllm_by_id
from CSI.vul_database_manage.vul_knowledge_tool import get_knoledge



from CSI.tool_manage.tool_use import make_agent_tool ,get_tool_list
from CSI.sql_database_manage.sql_database_use import Create_CSIsession

need_doc="""
        你是一个网络安全测试员，有着丰富的安全工具和流程经验，
        系统会提供给你安全工具和知识库，请优先在知识库中搜索任务和对应知识，需要你：
        1.使用工具完成对网站的调查，工具使用时请尽量使用消耗小不会超时的指令，避免系统卡顿
        2.依据工具结果推理，判断是否继续使用工具进一步测试
        3.如果认为测试很透彻了，可以结束工具使用，生成200字的测试报告
        4.只能使用toolcalling的方式调用工具，不能用自然语言的方式调用工具
        """






#初始化操作工具表格的session
CSI_session=Create_CSIsession()

id=1#默认使用id为1的LLM配置信息，可以修改为其他id

chosen_LLM=queryllm_by_id(CSI_session,id)
LLM=connectted_LLM(key=chosen_LLM.key,url=chosen_LLM.url,model=chosen_LLM.model,provider=chosen_LLM.provider)


#查询工具表格，返回一个tool的列表
tool_infos=get_tool_list(CSI_session)

#遍历列表，创建工具，加入agent_tool列表
agent_tools=[]
agent_tools.append(get_knoledge)




for tool_info in tool_infos:
    agent_tool=make_agent_tool(tool_info.name,tool_info.address,tool_info.description)
    agent_tools.append(agent_tool)




security_agent = create_security_agent(LLM,agent_tools,need_doc)


if __name__ == "__main__":
    #调用Agent进行安全评估
    result = security_agent.invoke({
        "messages": [{
            "role": "user", 
            "content": f"""
            除了合格标准的工具调用格式和报告生成外不许回复其他任何内容！
            目标网站的url需要你调用知识库工具查询，查询后
            系统会提供给你安全工具和知识库，对该网站地址进行安全测试，你需要：
            1.使用工具完成对网站的调查，工具使用时请尽量使用消耗小不会超时的指令，避免系统卡顿
            2.依据工具结果推理，判断是否继续使用工具进一步测试
            3.如果认为测试很透彻了，可以结束工具使用，生成200字的测试报告
            4.只能使用toolcalling的方式调用工具，不能用自然语言的方式调用工具
            5.一定要看一下网页的源码页面面，看看有没有什么有用的信息
            """
             }
        ]
    })
    print(result)

