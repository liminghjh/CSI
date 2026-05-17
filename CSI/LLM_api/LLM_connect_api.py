from fastapi import APIRouter,Body,Depends,HTTPException
from sqlalchemy.orm import Session
from CSI.LLM_api.LLM_connect import add_LLM_info, get_LLM_info_list, delete_LLM_info, LLM_is_reachable
from CSI.sql_database_manage.sql_database_use import get_CSIsession

LLM_router = APIRouter()


@LLM_router.get("/LLM_list",summary="获取配置信息",tags=["LLM"])
async def get_LLM_list(CSI_session:Session=Depends(get_CSIsession)):
    try:
        LLM_info=get_LLM_info_list(CSI_session)
        LLM_list=[]
        for LLM in LLM_info:
            LLM_dict={
                "id":LLM.id,
                "name":LLM.name,
                "provider":LLM.provider,
                "key":LLM.key,
                "url":LLM.url,
                "model":LLM.model
                }
            LLM_list.append(LLM_dict)
        return LLM_list
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
#示例如下
"""
[
    {
        "id": 1,
        "provider": "OpenAI",
        "name": "我的LLM配置",
        "url": "https://api.openai.com/v1/chat/completions",
        "model": "gpt-3.5-turbo",
        "key": "sk-xxxxxx"
    },
    {
        "id": 2,
        "provider": "Azure",
        "name": "Azure上的LLM配置",
        "url": "https://myazureendpoint.openai.azure.com/openai/deployments/mydeployment/chat/completions?api-version=2024-06-01",
        "model": "gpt-4o",
        "key": "azure_key_xxxxxx"
    }
]
"""

@LLM_router.post("/add",summary="添加LLM配置信息",tags=["LLM"])
async def add_LLM(
    CSI_session:Session=Depends(get_CSIsession),
    name=Body(...,description="LLM配置名"),
    provider=Body(...,descrition="LLM提供商"),
    key=Body(...,description="LLM密钥"),
    url=Body(...,description="LLM连接地址"),
    model=Body(...,description="LLM使用的模型")):
    try:
        add_LLM_info(CSI_session,LLM_name=name,LLM_provider=provider,LLM_key=key,LLM_url=url,LLM_model=model)
        return {"message":"LLM配置信息添加成功"}
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    

@LLM_router.post("/delete",summary="删除LLM配置信息",tags=["LLM"])
async def delete_LLM(
    CSI_session:Session=Depends(get_CSIsession),
    id:int=Body(...,description="LLM配置信息id")):
    try:
        delete_LLM_info(CSI_session,id)
        return {"message":"LLM配置信息删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))

#如果成功返回true否则返回false
@LLM_router.post("/test",summary="LLM配置连接测试",tags=["LLM"])
async def test_LLM(
    CSI_session:Session=Depends(get_CSIsession),
    id=Body(...,description="LLM表中的id")):
    try:
        result=LLM_is_reachable(CSI_session,LLM_id=id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))