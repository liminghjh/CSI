

from langchain.chat_models import init_chat_model

from sqlalchemy.orm import declarative_base 
from sqlalchemy import Column,Integer,String

from langchain.agents import create_agent


#创建安全评估Agent,默认使用配置文件中的工具
#需要传入参数，模型，工具，系统提示语
def create_security_agent(Aimodel=None, AItools=None, system_prompt=None):
    security_agent = create_agent(
        model=Aimodel,
        tools=AItools,
        system_prompt=system_prompt 
        )
    return security_agent


#创建大模型信息基类
LLM_base=declarative_base()

class LLM_info(LLM_base):
    __tablename__ = "LLM_info"
    id=Column(Integer, primary_key=True,autoincrement=True)#id号自增,主键
    name=Column(String,nullable=False)#配置的名字，不能为空
    provider=Column(String, nullable=False)#提供商,不能为空
    key=Column(String)#密钥可以空（ollama）
    url=Column(String,nullable=False)#api请求地址不能空
    model=Column(String,nullable=False)#模型，不能空

#新建llm配置表
def create_LLM_info_table(database)->bool:
    # 创建metadata下注册的所有表
    LLM_info.metadata.create_all(database)
    return True


#查询所有LLM表的信息，返回一个包含LLM_info对象的列表
def get_LLM_info_list(created_session):
    LLM_info_list=created_session.query(LLM_info).all()
    return LLM_info_list

#新建LLM配置信息
def add_LLM_info(created_session,LLM_name:str,LLM_provider:str,LLM_key:str,LLM_url:str,LLM_model:str):
    need_info=LLM_info(name=LLM_name,provider=LLM_provider,key=LLM_key,url=LLM_url,model=LLM_model)
    created_session.add(need_info)
    #真正执行
    created_session.commit()
    print(f"llm配置信息{LLM_name}添加完成")
    return True

#删除LLM配置信息（通过id）
def delete_LLM_info(created_session,LLM_id:Integer):
    #查询id符合的信息
    deleted_LLM_info=queryllm_by_id(created_session,LLM_id)
    created_session.delete(deleted_LLM_info)
    #真正执行删除
    created_session.commit()
    print("删除成功")
    return True


def queryllm_by_id(created_session,LLM_id:int):
    chosen_LLM_info=created_session.query(LLM_info).filter_by(id=LLM_id).first()
    return chosen_LLM_info


#测试LLM配置信息能不能联通
def LLM_is_reachable(created_session,LLM_id:int)->bool:
    chosen_LLM=created_session.query(LLM_info).filter_by(id=LLM_id).first()
    try:
        LLM=connectted_LLM(key=chosen_LLM.key,url=chosen_LLM.url,model=chosen_LLM.model,provider=chosen_LLM.provider)
        response=LLM.invoke("测试配置是否连接成功，只需要回复“收到”即可")
        print(response)
        return True
    except Exception as e:
        print(f"连接失败: {e}")
        return False





#与LLM建立连接，默认用配置文件中的信息
def connectted_LLM(key: str, url: str, model: str,provider: str):
    LLM=init_chat_model(
        api_key=key,
        base_url=url,
        model=model,
        model_provider=provider
        )
    return LLM