from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from CSI.config import sql_database_dir,sql_database_name

# 连接数据库
CSI_database=create_engine(f'sqlite:///{sql_database_dir}/{sql_database_name}')

#创建session操作类
Create_CSIsession=sessionmaker(bind=CSI_database)


#对于fastapi中的需要created_session用下面的方式结合fastapi的自动回收机制做到用完即收
def get_CSIsession():
    CSI_session=Create_CSIsession()#实例化操作session
    try:
        yield CSI_session
    finally:
        CSI_session.close()



if __name__ == "__main__":
    #初始化所有表
    from CSI.tool_manage.tool_use import create_tools_table
    from CSI.LLM_api.LLM_connect import create_LLM_info_table
    create_tools_table(CSI_database)
    create_LLM_info_table(CSI_database)
