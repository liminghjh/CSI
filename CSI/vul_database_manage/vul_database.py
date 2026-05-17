from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from CSI import config
from CSI.config import database_name,vector_database_dir,embedding_api_url,embedding_api_key,embedding_model
import requests
import os
from typing import List#高版本中不需要导入List，用于->List[float]的类型提示

#文档加载器（加载目录下的文件）
loader = DirectoryLoader(
    config.knowledge_dir,  # 替换为你的目录路径
    glob="**/*.md",     #不默认遍历读取目录下文件
    loader_cls=TextLoader,
    loader_kwargs={"encoding": "utf-8"}
)

#单个文件加载器
def one_loader(file_path:str):
    a_loader = TextLoader(file_path,encoding="utf-8")
    return a_loader

#分片器
data_splitter = RecursiveCharacterTextSplitter(
    chunk_size=config.chunk_size,  # 每个片段的最大长度
    chunk_overlap=config.chunk_overlap,  # 片段之间的重叠长度
    separators=["\n\n", "\n", "。", "，","！", "？", "；", " ", "",".",",","!","?"]  #分割符列表，优先级从高到低
)

"""需要加入异常处理机制"""
#兼容nvdia的embedding类
class NvidiaEmbedding:
    def __init__(self,Embedding_API_URL,Embedding_API_KEY,Embedding_MODEL):#需要传入API的URL、KEY和模型名称
        self.url = Embedding_API_URL
        self.key = Embedding_API_KEY
        self.model = Embedding_MODEL
    
    def embed_query(self,chunk:str)->List[float]:
        request_url = self.url  #自带所有路径如https://integrate.api.nvidia.com/v1/embeddings
        headers={
            "Authorization": "Bearer " + self.key,
            "Content-Type": "application/json"
            }
        json_data = {
            "model": "nvidia/nv-embed-v1",
            "input": [chunk]  # 注意是数组格式,可以传入多个文本进行批量处理
        }
        response = requests.post(request_url,headers=headers,json=json_data)
        array = response.json()["data"][0]["embedding"]#提取第一个embedding向量
        return array
    
    def embed_documents(self,chunks:List[str])->List[List[float]]:
        request_url = self.url  #自带所有路径如https://integrate.api.nvidia.com/v1/embeddings
        headers={
            "Authorization": "Bearer " + self.key,
            "Content-Type": "application/json"
            }
        json_data = {
            "model": self.model,
            "input": chunks  # 注意是数组格式,可以传入多个文本进行批量处理
        }
        response = requests.post(request_url,headers=headers,json=json_data)

        Embed_chunks = []
        for i in range(len(chunks)):#提取每个文本对应的embedding向量
            array = response.json()["data"][i]["embedding"]
            Embed_chunks.append(array)
        return Embed_chunks


#初始化的nvdia_embedding实例
nvdia_embedding=NvidiaEmbedding(embedding_api_url, embedding_api_key, embedding_model)

#初始化向量数据库,入参：分片后的文档、embedding实例、数据库名字、数据库存放目录
def initialize_vector_database(splited_documents,embedding,database_name,vertory_database_dir):
    vector_db =Chroma.from_documents (
    documents=splited_documents,
    embedding=embedding,#传入embedding实例
    collection_name=database_name,#这个向量数据库的名字
    persist_directory=vertory_database_dir#本地存放向量数据库的目录
    )
    return vector_db

#载入已经有的向量数据库
def load_vector_database(embedding,database_name,vector_database_dir):
    vector_db = Chroma(#加载本地数据库
    collection_name=database_name,
    persist_directory=vector_database_dir,
    embedding_function=embedding
    )
    return vector_db

#根据输入的问题，在向量数据库中进行相似度检索，返回最相关的前几个片段
def get_similar_documents(query:str,vector_db,get_back_number:int):#返回的是List[Document]类型
    similar_documents = vector_db.similarity_search(query, k=get_back_number)
    return similar_documents


#给出一个地址，循环返回dict结构
'''结构如下
dict:{
path_name:
dirs:[dict:{
}]
files:[]
}
'''
def show_vul_database (address):
    database_dict={}
    database_dict["path_name"]=address
    database_dict["dirs"]=[]
    database_dict["files"]=[]
    for item in os.listdir(address):
        sub_address=os.path.join(address,item)

        if(os.path.isdir(sub_address)):
            database_dict["dirs"].append(show_vul_database(sub_address))
        else:
            database_dict["files"].append(item)

    return database_dict

#给出一个文件的地址和数据库，把改文件加入向量数据库
def add_vul_database(file_address:str,vector_db):
    file_loader=one_loader(file_address).load()#导入文件，返回一个list[document]
    chunks=data_splitter.split_documents(file_loader)#进行分片
    ids=vector_db.add_documents(chunks)#添加文档，返回添加的片段在库中的id
    print("添加成功，新建的片段的id如下：",f"{ids}")
    return ids#返回片段的id值


#给出一个文件地址，在向量库中查询source栏下的值并删除
def delete_vul_database(file_address:str,vector_db):
    vector_db.delete(where={"source":file_address})
    print("文件从向量库中删除")









if __name__=="__main__":
    print("正在初始化数据库")
    #加载文档md->document
    data_documents = loader.load()
    
    #分片document文档
    splited_documents = data_splitter.split_documents(data_documents)
    #先初始化向量数据库
    nvdia_embedding=NvidiaEmbedding(config.embedding_api_url, config.embedding_api_key, config.embedding_model)

    vector_database=initialize_vector_database(splited_documents,nvdia_embedding,database_name,vector_database_dir)
    print("成功初始化知识库")
