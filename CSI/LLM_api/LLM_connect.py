
#获取api信息
from CSI.config import api_key, api_url, api_model, api_provider

from langchain.chat_models import init_chat_model


# 创建LLM信息类，默认用配置文件中的信息
class LLM_information:
    def __init__(self, key: str, url: str, model: str,provider:str):
        self.key = key if key else api_key
        self.url = url if url else api_url
        self.model = model if model else api_model
        self.provider = provider if provider else api_provider

#与LLM建立连接，默认用配置文件中的信息
def connectted_LLM(key=api_key, url=api_url, model=api_model,provider=api_provider):
    LLM=init_chat_model(
        api_key=key,
        base_url=url,
        model=model,
        model_provider=provider
        )
    return LLM