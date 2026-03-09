

#定义一个工具类，包括工具名称、工具描述和工具地址
class classtool:

    def __init__(self,name : str=None,description:str=None,address:str=None,toolfunc=None):
        self.name=name
        self.description=description
        self.address=address
        self.toolfunc=toolfunc

    #定义一个方法来生成ai工具，接受一个函数和参数，并返回工具的使用结果(结果为字符串输出)



