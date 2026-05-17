# 配置文件

import os

# 项目目录配置
project_dir = os.path.dirname(os.path.abspath(__file__))    # 项目根目录->CSI的目录绝对路径


#默认大语言模型信息
api_key=""                    # 你的API key
api_url="https://integrate.api.nvidia.com/v1"                   # API地址
api_model="openai/gpt-oss-120b"                     # 模型名称 
api_provider="openai"                     # 模型提供商
# api_key=""                    # 你的API key
# api_url="http://28.0.0.1:11434/v1"                   # API地址
# api_model="functiongemma:270m"                     # 模型名称 
# api_provider="openai" 


#embedding模型配置信息
embedding_api_url = "https://integrate.api.nvidia.com/v1/embeddings"  # 替换为实际 NVIDIA API URL
embedding_api_key = ""  # 替换为实际 API Key
embedding_model = "nvidia/nv-embed-v1"


#知识库相关配置
knowledge_dir = project_dir + "/vul_database_manage/vul_database"  # 知识库目录
vector_database_dir=project_dir+"/vul_database_manage/vector_database"
database_name="vul_database" #向量数据库的名字
chunk_size=500 #文本切分的块大小
chunk_overlap=50 #文本切分的重叠部分大小
get_back_number=2#召回片段的数量


#tools配置相关
tools_config = ["nmap", "sqlmap", "curl","vul_knowledge"]  # 可用工具列表



#SQL数据库相关配置
sql_database_dir = f"{project_dir}/sql_database_manage/SQL_database"  # SQL数据库URL
sql_database_name="CSI.db" #SQL数据库名字

#执行相关
max_turn=50 #最大对话轮数