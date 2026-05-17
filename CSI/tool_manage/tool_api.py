from fastapi import APIRouter,Body,Depends,HTTPException
from sqlalchemy.orm import Session
from CSI.tool_manage.tool_use import add_tool, get_tool_list, delete_tool
from CSI.sql_database_manage.sql_database_use import get_CSIsession
tool_router = APIRouter()


@tool_router.get("/tools_list",summary="获取工具列表",tags=["tool"])
async def get_tools_list(CSI_session:Session=Depends(get_CSIsession)):
    try:
        tool_info = get_tool_list(created_session=CSI_session)#返回一个包含Tools对象的列表
        tool_list=[]
        for tool in tool_info:
            tool_dict={
                "id":tool.id,
                "name":tool.name,
                "address":tool.address,
                "description":tool.description
                }
            tool_list.append(tool_dict)
        return tool_list#返回json格式
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
"""示例如下
[
    {
        "id": 1,
        "name": "锤子",
        "address": "仓库A",
        "description": "羊角锤"
    },
    {
        "id": 2,
        "name": "螺丝刀",
        "address": "仓库B",
        "description": "十字螺丝刀"
    }
]
"""



@tool_router.post("/add",summary="添加工具",tags=["tool"])
async def add_tools(
    CSI_session:Session=Depends(get_CSIsession),
    tool_name:str=Body(...,description="工具名字"),#不能为空
    tool_address:str=Body(...,description="工具存放地址"),
    tool_description:str=Body(...,description="工具描述文件")):
    try:
        add_tool(CSI_session,tool_name,tool_address,tool_description)
        return {"message": "工具添加成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#直接传入id数字不要字典
@tool_router.post("/delete",summary="删除工具",tags=["tool"])
async def delete_tool_column(
    CSI_session:Session=Depends(get_CSIsession),
    tool_id:int=Body(...,description="工具id")):

    try:
        delete_tool(CSI_session,tool_id)
        return {"message": "工具删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

