import requests
import random
import re
import json
import logging
import time
from bs4 import BeautifulSoup
from userAgent import user_agent_list
from nameMap import country_type_map, city_name_map, country_name_map, continent_name_map




def crawler_test():
    # 会话信息
    session = requests.session()
    # 设置不同的请求头
    session.headers.update(
        {
            'user-agent':random.choice(user_agent_list)
        }
    )
    # print(session.headers)

    # 发起请求 
    try:
        r = session.get(url='https://ncov.dxy.cn/ncovh5/view/pneumonia')
    except requests.exceptions.ChunkedEncodingError:
        pass
    # print(r.content)

    # 解析请求
    soup = BeautifulSoup(r.content, 'lxml')
    # print(soup)

    # 正则表达式，搜索数据脚本
    overall_information = re.search(r'(\{"id".*\})\}', str(soup.find('script', attrs={'id': 'getStatisticsService'})))
    print(overall_information)

    # 解析数据
    overall_information = json.loads(overall_information.group(1))
    overall_information.pop('id')
    overall_information.pop('createTime')
    overall_information.pop('modifyTime')
    overall_information.pop('imgUrl')
    overall_information.pop('deleted')
    overall_information['countRemark'] = overall_information['countRemark'].replace(' 疑似', '，疑似').replace(' 治愈', '，治愈').replace(' 死亡', '，死亡').replace(' ', '')

    # print(overall_information)


class DXYCrawler:
    def __init__(self):
        logging.info("crawler test")
        # 爬取数据的时间戳
        self.crawl_timestamp = int()
        # 爬取数据的会话
        self.session = requests.session()
        self.session.headers.update(
            {
                'user-agent': random.choice(user_agent_list)
            }
        )
        # 爬取时间
        self.crawl_timestamp = int(time.time() * 1000)
        # 开始爬取
        try:
            r = self.session.get(url='https://ncov.dxy.cn/ncovh5/view/pneumonia')
        except requests.exceptions.ChunkedEncodingError:
            logging.error('Crawler Failed : Network error')
            pass
        self.soup = BeautifulSoup(r.content, 'lxml') #bs4.BeautifulSoup
    

    def overall_parser(self):
        # 正则匹配数据
        overall_result = re.search(r'(\{"id".*\})\}', str(self.soup.find('script', attrs={'id': 'getStatisticsService'})))
        if overall_result:
            # 匹配数据转为字典
            overall_dict = json.loads(overall_result.group(1))
            # 整理全球和国内数据
            overall_information = dict()
            statistics = [{
                # 中国疫情数据
                'currentConfirmedCount': overall_dict.get('currentConfirmedCount','缺失数据'), 
                'confirmedCount': overall_dict.get('confirmedCount','缺失数据'), 
                'suspectedCount':overall_dict.get('suspectedCount','缺失数据'),
                'curedCount': overall_dict.get('curedCount','缺失数据'), 
                'deadCount': overall_dict.get('deadCount','缺失数据'),
                'seriousCount':overall_dict.get('seriousCount','缺失数据'),
                'currentConfirmedIncr': overall_dict.get('currentConfirmedIncr','缺失数据'), 
                'confirmedIncr': overall_dict.get('confirmedIncr','缺失数据'), 
                'suspectedIncr':overall_dict.get('suspectedIncr','缺失数据'),
                'curedIncr': overall_dict.get('curedIncr','缺失数据'), 
                'deadIncr': overall_dict.get('deadIncr','缺失数据'),
                'seriousIncr':overall_dict.get('seriousIncr','缺失数据'),
                # 世界疫情数据
                'globalStatistics':overall_dict.get('globalStatistics','缺失数据'),
                'crawlTime':self.crawl_timestamp
            }]
            overall_information['results'] = statistics
            return overall_information
        # 若爬取失败
        return None


    def province_parser(self):
        province_result = re.search(r'\[(.*)\]', str(self.soup.find('script', attrs={'id': 'getAreaStat'})))
        if province_result:
            province_list = json.loads(province_result.group(0))
            province_information = dict()
            provinces = list()
            for province in province_list:
                # 移除无用信息
                province.pop('statisticsData')
                # 地区添加额外信息
                province['countryName'] = '中国'
                province['countryEnglishName'] = 'China'
                province['continentName'] = '亚洲'
                province['continentEnglishName'] = 'Asia'
                province['provinceEnglishName'] = city_name_map[province['provinceShortName']]['engName']

                for city in province['cities']:
                    if city['cityName'] != '待明确地区':
                        try:
                            city['cityEnglishName'] = city_name_map[province['provinceShortName']]['cities'][city['cityName']]
                        except KeyError:
                            # print(province['provinceShortName'], city['cityName'])
                            pass
                    else:
                        city['cityEnglishName'] = 'Area not defined'

                province['crawlTime'] = self.crawl_timestamp
                provinces.append(province)
            province_information['results'] = provinces
            return province_information
        # 若爬取失败
        return None
    

    def abroad_parser(self):
        abroad_result = re.search(r'\[(.*)\]', str(self.soup.find('script', attrs={'id': 'getListByCountryTypeService2true'})))
        if abroad_result:
            country_list = json.loads(abroad_result.group(0))
            country_information = dict()
            countries = list()
            for country in country_list:
                try:
                    country.pop('id')
                    country.pop('tags')
                    country.pop('sort')
                    # Ding Xiang Yuan have a large number of duplicates,
                    # values are all the same, but the modifyTime are different.
                    # I suppose the modifyTime is modification time for all documents, other than for only this document.
                    # So this field will be popped out.
                    country.pop('modifyTime')
                    # createTime is also different even if the values are same.
                    # Originally, the createTime represent the first diagnosis of the virus in this area,
                    # but it seems different for abroad information.
                    country.pop('createTime')
                    country['comment'] = country['comment'].replace(' ', '')
                except KeyError:
                    pass
                country.pop('countryType')
                country.pop('provinceId')
                country.pop('cityName')
                country.pop('statisticsData')
                # The original provinceShortName are blank string
                country.pop('provinceShortName')
                # Rename the key continents to continentName
                country['continentName'] = country.pop('continents')
                # 新增信息
                country['countryName'] = country.get('provinceName')
                country['provinceShortName'] = country.get('provinceName')
                country['continentEnglishName'] = continent_name_map.get(country['continentName'])
                country['countryEnglishName'] = country_name_map.get(country['countryName'])
                country['provinceEnglishName'] = country_name_map.get(country['countryName'])
                country['crawlTime'] = self.crawl_timestamp
                countries.append(country)
            
            country_information['results'] = countries
            return country_information
        # 若爬取失败
        return None

    
    def news_parser(self):
        # 正则匹配
        news_chinese_result = re.search(r'\[(.*?)\]', str(self.soup.find('script', attrs={'id': 'getTimelineService1'})))
        if news_chinese_result:
            # 匹配数据转为字典
            news_chinese_list = json.loads(news_chinese_result.group(0))
            news_information = dict()
            news_cn = list()
            for news in news_chinese_list:
                # 移除无用信息
                news.pop('provinceId')
                news['crawlTime'] = self.crawl_timestamp
                news_cn.append(news)
            news_information['results'] = news_cn
            return news_information 
        # 若爬取失败
        return None

        # news_english = re.search(r'\[(.*?)\]', str(self.soup.find('script', attrs={'id': 'getTimelineService2'})))
        # if news_english:
        #     new_en = json.loads(news_english.group(0))
        #     return new_en


    def rumor_parser(self):
        # 正则匹配
        rumors_result = re.search(r'\[(.*?)\]', str(self.soup.find('script', attrs={'id': 'getIndexRumorList'})))
        if rumors_result:
            # 匹配数据转字典
            rumors_list = json.loads(rumors_result.group(0))
            rumors_information = dict()
            rumors = list()
            for rumor in rumors_list:
                # 移除无用信息
                rumor.pop('summary')
                rumor.pop('sourceUrl')
                rumor.pop('score')
                rumor['crawlTime'] = self.crawl_timestamp
                rumors.append(rumor)
            rumors_information['results'] = rumors
            return rumors_information
        # 若爬取失败
        return None



if __name__ == "__main__":
    # crawler_test()

    # d_test = DXYCrawler()

    # 中国和全球疫情概况
    # o1 = d_test.overall_parser()
    # print(o1)
    
    # 新闻和谣言
    # n1 = d_test.news_parser()
    # n1 = json.dumps(n1)
    # print(n1)
    # r1 = d_test.rumor_parser()
    # r1 = json.dumps(r1)
    # print(r1)

    # 各省份概况
    # p1 = d_test.province_parser()
    # p1 = json.dumps(p1)
    # print(p1)

    # 各国概况
    # a1 = d_test.abroad_parser()
    # a1 = json.dumps(a1)
    # print(a1)
    pass

    