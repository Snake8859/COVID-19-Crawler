# 丁香园疫情信息实时接口

2019新型冠状病毒（COVID-19/2019-nCoV）疫情信息实时接口，数据来源于[丁香园](https://3g.dxy.cn/newh5/view/pneumonia)。

基于FastAPI+疫情数据爬虫实现。

核心文件说明：

- main.py ：启动项

- dxy_crawler.py：疫情数据爬虫

- nameMap.py和userAgent.py：辅助数据

接口说明：

- http://127.0.0.1:8866/docs （接口测试和说明入口）

- http://127.0.0.1:8866/covid-19/overall  （全球和中国疫情概况接口）
- http://127.0.0.1:8866/covid-19/province （中国各省疫情信息接口）
- http://127.0.0.1:8866/covid-19/abroad （世界各国疫情概况）
- http://127.0.0.1:8866/covid-19/news （疫情相关新闻接口）
- http://127.0.0.1:8866/covid-19/rumor （疫情相关谣言接口）

使用说明：

> 利用requirements.txt和conda创建运行环境：
>
> conda create --name <env> --file requirements.txt
>
> 启动接口：
>
> python main.py

感谢[**2019新型冠状病毒疫情实时爬虫**](https://github.com/BlankerL/DXY-COVID-19-Crawler)项目，本项目接口代码在此基础上改造而成。

