from fastapi import FastAPI,Body
from fastapi.responses import StreamingResponse
from CSI.vul_database_manage.vul_database_api import vul_database_router
from CSI.tool_manage.tool_api import tool_router
from CSI.LLM_api.LLM_connect_api import LLM_router

from CSI.config import max_turn

from CSI.LLM_api.LLM_connect import connectted_LLM,create_security_agent,queryllm_by_id
from CSI.vul_database_manage.vul_knowledge_tool import get_knoledge
from CSI.tool_manage.tool_use import make_agent_tool ,get_tool_list
from CSI.sql_database_manage.sql_database_use import Create_CSIsession


from CSI.prompt.report_maker import report_prompt,reporter_model
from CSI.prompt.flag_taker import take_flag_prompt,flag_parser

import json

app = FastAPI()
app.include_router(tool_router, prefix="/tool", tags=["tool"])
app.include_router(LLM_router, prefix="/LLM", tags=["LLM"])
app.include_router(vul_database_router, prefix="/vul_database", tags=["vul_database"])

start_message={
    "type":"start",
    "message":"开始运行任务"
}

prepare_agent={
    "type":"prepare",
    "message":"完成环境准备"
}



@app.post("/start_task",summary="开启安全探测任务",tags=["task"])
async def start_task_stream (

        url_or_ip:str=Body(...,description="输入目标网站的url或者ip地址"),
        port:int=Body(None,description="输入目标网站的端口号"),#端口号不是必须的
        LLM_id:int=Body(...,description="选择LLM配置文件"),
        system_doc:int=Body(...,description="选择完成的任务类型,0是生成报告，1是获取flag值")):

    async def stream_output():
        try:

            #发出开始的信息
            yield "data: "+json.dumps(start_message,ensure_ascii=False)+ "\n\n"


            #初始化操作工具表格的session
            CSI_session=Create_CSIsession()
            id=LLM_id
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
            
            #根据system_doc选择系统消息
            #当system_doc=0时，选择生成报告的系统消息
            if system_doc==0:
                prompt=report_prompt
                input_context={
                    "messages": [{
                        "role": "user", 
                        "content": f"""请对目标 {url_or_ip}:{port} 进行全面的安全评估，识别潜在的漏洞和风险，并生成一份专业的安全检测报告。 
                        """
                        }
                    ]
                }
                chosen_agent = create_security_agent(LLM,agent_tools,prompt)
            #当system_doc=1时，选择夺取flag的系统消息
            elif system_doc==1:
                prompt=take_flag_prompt
                input_context={
                    "messages": [{
                        "role": "user", 
                        "content": f"""请对目标 {url_or_ip}:{port} 进行全面的安全评估，识别潜在的漏洞和风险，并尝试夺取隐藏的Flag值 
                        """
                        }
                    ]
                }
                chosen_agent = create_security_agent(LLM,agent_tools,prompt)

            #发送准备好agent信息
            yield "data: "+json.dumps(prepare_agent,ensure_ascii=False)+ "\n\n"
            final_content = None  # 存候选内容，后面有新的就覆盖


            async for message in chosen_agent.astream_events(
                    version="v2",#最新版本支持根据输出标签行动
                    input=input_context,
                    config={"recursion_limit": max_turn}
                    ):

                    #根据message的event类型，发送不同的信息给前端
                    #当工具开始执行时，发送工具输入信息
                    if  message["event"]=="on_tool_start":
                        yield "data: "+json.dumps(
                            {
                                "type":"start_tool",
                                "message": str(message["data"].get("input",{})),
                                "tool":message["name"]
                            },ensure_ascii=False
                        )+ "\n\n"
                    #当工具执行结束时，发送工具输出结果
                    elif message["event"]=="on_tool_end" :
                        yield "data: "+json.dumps(
                            {
                                "type":"end_tool",
                                "message": str(message["data"].get("output"," ")),
                                "tool":message["name"]
                            },ensure_ascii=False
                        )+ "\n\n"
                    #当链路执行结束时，发送最终结果
                    elif message["event"]=="on_chain_end":
                        result=message["data"].get("output",{})
                        if isinstance(result, dict) and "messages" in result:
                            msgs = result["messages"]
                            if msgs:
                                last_msg = msgs[-1]
                                if last_msg.type == "ai" and not last_msg.tool_calls:
                                    final_content = last_msg.content
            if  final_content:                   
                print("所有结果:" ,str(final_content))
                if system_doc==0:
                    report=reporter_model.parse(final_content)
                else:
                    report=flag_parser.parse(final_content)
                yield "data: "+json.dumps(
                    {
                    "type":"report",
                    "message":str(report)
                    },ensure_ascii=False
                )+ "\n\n"
            else:
                yield "data: "+json.dumps(
                    {
                    "type":"report",
                    "message":"未能生成有效的结果"
                    },ensure_ascii=False
                )+ "\n\n"


        except Exception as e:

            yield "data: " + json.dumps({"type": "error", "message": str(e)}, ensure_ascii=False) + "\n\n"

        finally:
            CSI_session.close()


    return StreamingResponse(
        stream_output(),
        media_type="text/event-stream"
    )



if __name__ == "__main__":
    print("开启CSI项目后端在8000端口")

    import uvicorn
    uvicorn.run(app , host="0.0.0.0", port=8000)