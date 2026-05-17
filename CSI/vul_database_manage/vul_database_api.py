from fastapi import APIRouter,UploadFile,File,Form,Body,HTTPException
from CSI.vul_database_manage.vul_database import show_vul_database,add_vul_database,delete_vul_database,nvdia_embedding,load_vector_database
from CSI.config import database_name,vector_database_dir,knowledge_dir
import json
import os
vul_database_router = APIRouter()

@vul_database_router.get("/database_list",summary="获取数据库的文件", tags=["vul_database"])
async def get_vul_list():
    try:
        result=show_vul_database(knowledge_dir)
        json_result=json.dumps(result)
        return json_result
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))

@vul_database_router.post("/upload",summary="将文件新增到向量数据库和本地文件", tags=["vul_database"])
async def add_vul_file(file_addr:str=Form(...,description="传入文件想要保存的目录"),#由于上传的是表单，不能和json并存，所以我们传入文件目录用的也是Form表单形式
                       file:UploadFile=File(...,description="传入的文件")):
    try:
        content=await file.read()
        with open(os.path.join(file_addr,file.filename),"wb")as f:
            f.write(content)
        vector_db=load_vector_database(nvdia_embedding,database_name,vector_database_dir)
        ids=add_vul_database(os.path.join(file_addr,file.filename),vector_db)
        return {"message":"文件上传成功","ids":ids}
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))




@vul_database_router.post("/delete",summary="根据文件的路径和名字从向量库中删除", tags=["vul_database"])
async def delete_vul_file(file_addr:str=Body(...,description="文件的路径"),
                          file_name:str=Body(...,description="需要删除的文件名")):
    try:
        file_add_name=os.path.join(file_addr,file_name)
        vector_db=load_vector_database(nvdia_embedding,database_name,vector_database_dir)
        delete_vul_database(file_add_name,vector_db)
        os.remove(file_add_name)
        return {"message":"文件删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))

