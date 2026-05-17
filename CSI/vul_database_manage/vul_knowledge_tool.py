from langchain.tools import tool
from CSI.vul_database_manage.vul_database import nvdia_embedding,load_vector_database,get_similar_documents
from CSI.config import database_name,vector_database_dir,get_back_number
import threading

"""
工具名称：vul_knowledge
工具描述：一个漏洞知识库，对特殊漏洞的信息进行补充，指导完成测试工作
"""


tool_name = "vul_knowledge"
tool_description = "一个漏洞知识库，对输入的内容进行相似度检索，返回最相关的前几个片段，注意不是所有都有用的"


"""需要加入异常处理机制"""
"""需要完成判断是否存在向量数据库跳过初始化的问题"""

# 创建一个线程锁对象
vector_db_lock = threading.Lock() 

@tool(tool_name, description=tool_description)
def get_knoledge(question: str) ->str:
    with vector_db_lock:  # 在访问向量数据库时获取锁，确保线程安全
        print("输入的问题是："+question)
        print("载入数据库")
        #载入向量数据库
        vector_database=load_vector_database(nvdia_embedding,database_name,vector_database_dir)
        #余弦相似度计算方法
        similar_documents=get_similar_documents(question,vector_database,get_back_number)
        #拼接成大模型可以理解的str文本形式
        answers="知识库的相关片段如下：" 
        Index=1
        for i in similar_documents:
            answers=answers+" "+f"{Index}"+i.page_content
            Index+=1
        print(answers)
        return answers





