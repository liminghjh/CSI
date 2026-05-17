from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String
from langchain.tools import tool
import subprocess
# 创建基类
Tools_base = declarative_base()
# 定义工具表
class Tools(Tools_base):
    __tablename__ = "tools"
    id = Column(Integer, primary_key=True,autoincrement=True)#id号自增,主键
    name = Column(String, nullable=False)#工具名称,不能为空
    address = Column(String)#工具地址
    description = Column(String)#工具描述



#创建tools表
def create_tools_table(database)->bool:
    # 创建metadata下注册的所有表
    Tools_base.metadata.create_all(database)
    return True



#添加工具数据
def add_tool(created_session,tool_name:str,tool_address:str=None,tool_description:str=None)->bool:#必须输入名字
    #创建一个工具数据
    tool_data=Tools(name=tool_name,address=tool_address,description=tool_description)
    #插入数据
    created_session.add(tool_data)
    #真正执行插入操作
    created_session.commit()
    print(f"工具{tool_name}添加成功！")
    return True


#查询所有工具数据，返回一个包含Tools对象的列表
def get_tool_list(created_session):
    tool_info=created_session.query(Tools).all()
    return tool_info

#删除某行信息，依据工具的id
def delete_tool(created_session,tool_id:int):
    #查询约束条件的数据,返回一个Tools对象
    deleted_tool_info=created_session.query(Tools).filter_by(id=tool_id).first()
    created_session.delete(deleted_tool_info)
    created_session.commit()
    print("删除成功")
    return True





#依据name、address、description等信息创建一个llm可以识别的工具函数，并返回
def make_agent_tool (tool_name:str,tool_addression:str,tool_description:str="一个工具"):
    @tool(tool_name,description=tool_description)#第一个参数默认是函数工具的名字
    def agent_tool(command:str)->str:#使用方法是传入一个指令
        print("开始使用工具：",tool_name)
        cmd=f"{tool_addression} {command}"
        print(f"执行指令：{cmd}")

        try:
            tool_execute=subprocess.run(cmd,text=True,start_new_session=True,timeout=15,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True,encoding="UTF-8")
            result =f"工具{tool_name}执行指令{command}的结果如下：{tool_execute.stdout} 执行发送的错误报错如下：{tool_execute.stderr}"
            print(result)
            return result
        except subprocess.TimeoutExpired as e:
            timeout_result=f"工具{tool_name}执行指令{command}超时，结果如下："
            if e.stdout:
                timeout_result +=e.stdout.decode("UTF-8")
            if e.stderr:
                timeout_result+=e.stderr.decode("UTF-8")
            print(timeout_result)
        except Exception as e:
            # 其他异常处理
            error_msg = f"工具{tool_name}执行失败：{str(e)}"
            print(error_msg)
            return error_msg
    return agent_tool
