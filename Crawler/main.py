import json

from fastapi import FastAPI,HTTPException,Request
#引入 CORS中间件模块
from starlette.middleware.cors import CORSMiddleware  
from dxy_crawler import DXYCrawler
# 日志初始化
import logging
logging.basicConfig(filename="dxy_crawler.log", 
                    filemode="a", 
                    format="%(asctime)s %(name)s:%(levelname)s:%(message)s", 
                    datefmt="%Y-%m-%d %H:%M:%S", 
                    level=logging.INFO)
# 关于访问日志记录添加

# 创建FastAPI实例对象
app = FastAPI()

#设置允许访问的域名
origins = ["*"]

#设置跨域传参
app.add_middleware(
    CORSMiddleware, 
    allow_origins=origins,  #设置允许的origins来源
    allow_credentials=True,
    allow_methods=["*"],  # 设置允许跨域的http方法，比如get、post、put等。
    allow_headers=["*"])  #允许跨域的headers,可以用来鉴别来源等作用。

# 访问的根目录
root_str = "/covid-19" 

@app.get(root_str)
async def read_root():
    return {"Hello":"This is the COVID-19 Data Service"}


@app.get(root_str+"/overall")
async def read_overall(request: Request):
    dxyC = DXYCrawler()
    overall_information = dxyC.overall_parser()
    if overall_information == None:
        error_handler("overall")
    logging_handler(request,'/overall')
    return overall_information


@app.get(root_str+"/province")
async def read_province(request: Request):
    dxyC = DXYCrawler()
    province_information = dxyC.province_parser()
    if province_information == None:
        error_handler("province")
    logging_handler(request,'/province')
    return province_information


@app.get(root_str+"/abroad")
async def read_abroad(request: Request):
    dxyC = DXYCrawler()
    abroad_information = dxyC.abroad_parser()
    if abroad_information == None:
        error_handler("abroad")
    logging_handler(request,'/abroad')
    return abroad_information


@app.get(root_str+"/news")
async def read_news(request: Request):
    dxyC = DXYCrawler()
    news_information = dxyC.news_parser()
    if news_information ==None:
        error_handler("news")
    logging_handler(request,'/news')
    return news_information


@app.get(root_str+"/rumor")
async def read_rumor(request: Request):
    dxyC = DXYCrawler()
    rumor_information = dxyC.rumor_parser()
    if rumor_information == None:
        error_handler("rumor")
    logging_handler(request,'/rumor')
    return rumor_information


def error_handler(crawl_type):
    raise HTTPException(status_code=500, detail="COVID-19 "+crawl_type+" Data Crawl failure")


def logging_handler(request,url):
    clientInfo = str(request.client.host)+":"+ str(request.client.port)
    logging.info(clientInfo+"get "+url)


if __name__ == "__main__":
    # 基于命令行启动：uvicorn main:app --host 0.0.0.0 --port 8000 --reload (热部署+自定义IP与端口)
    # 基于导入启动
    import uvicorn
    uvicorn.run(app,host='127.0.0.1',port=8866)