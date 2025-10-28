import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from fake_useragent import UserAgent
from datetime import datetime
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class FudanLectureScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        }
        self.lectures = []
        
    def get_random_sleep_time(self):
        """生成随机休眠时间，避免被反爬"""
        return random.uniform(2, 5)
        
    def scrape_fudan_official(self):
        """从复旦大学官方网站抓取讲座信息"""
        urls = [
            'https://www.fudan.edu.cn/en/lectures_1379/list.htm',  # 英文网站讲座信息
            'https://www.fudan.edu.cn/2018/index.html',  # 主页新闻通知
            'https://www.fudan.edu.cn/2018/ggtz1/index.html',  # 公告通知
            'https://www.fudan.edu.cn/2018/xsgz/index.html',  # 学生工作
        ]
        
        for url in urls:
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                response.encoding = 'utf-8'
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 根据不同页面结构提取讲座信息
                if 'lectures' in url:
                    # 英文网站讲座列表
                    lecture_items = soup.select('.list_right li')
                    for item in lecture_items:
                        try:
                            title = item.select_one('a').text.strip()
                            link = 'https://www.fudan.edu.cn' + item.select_one('a')['href']
                            date = item.select_one('.date').text.strip() if item.select_one('.date') else '未知'
                            
                            # 访问详情页获取更多信息
                            time.sleep(self.get_random_sleep_time())
                            detail_response = requests.get(link, headers=self.headers, timeout=10)
                            detail_response.encoding = 'utf-8'
                            detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
                            
                            # 提取时间和地点
                            content = detail_soup.select_one('.article').text if detail_soup.select_one('.article') else ''
                            location = '未知'
                            
                            # 添加到列表
                            self.lectures.append({
                                'title': title,
                                'date': date,
                                'location': location,
                                'source': 'Fudan Official Website',
                                'link': link
                            })
                        except Exception as e:
                            print(f"处理英文网站讲座项时出错: {e}")
                else:
                    # 其他中文页面
                    news_items = soup.select('.list_news li') + soup.select('.list_news1 li')
                    for item in news_items:
                        try:
                            title = item.text.strip()
                            # 筛选包含讲座关键词的条目
                            if any(keyword in title for keyword in ['讲座', '学术报告', '论坛', 'seminar', 'lecture']):
                                link = url.rsplit('/', 1)[0] + '/' + item.select_one('a')['href'] if item.select_one('a') else url
                                date = item.select_one('.date').text.strip() if item.select_one('.date') else '未知'
                                
                                # 访问详情页获取更多信息
                                time.sleep(self.get_random_sleep_time())
                                detail_response = requests.get(link, headers=self.headers, timeout=10)
                                detail_response.encoding = 'utf-8'
                                detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
                                
                                # 提取内容
                                content = detail_soup.select_one('.neirong').text if detail_soup.select_one('.neirong') else ''
                                content += detail_soup.select_one('.article').text if detail_soup.select_one('.article') else ''
                                
                                # 尝试从内容中提取时间和地点
                                location = '未知'
                                
                                # 添加到列表
                                self.lectures.append({
                                    'title': title,
                                    'date': date,
                                    'location': location,
                                    'source': 'Fudan Official Website',
                                    'link': link
                                })
                        except Exception as e:
                            print(f"处理中文网站新闻项时出错: {e}")
                
            except Exception as e:
                print(f"访问复旦大学官方网站 {url} 时出错: {e}")
                
            # 休眠一段时间
            time.sleep(self.get_random_sleep_time())
    
    def scrape_school_websites(self):
        """从复旦大学各学院网站抓取讲座信息"""
        school_urls = [
            'https://www.fdsm.fudan.edu.cn/info/1070/3611.htm',  # 管理学院讲座
            'https://www.physics.fudan.edu.cn/1732/list.htm',  # 物理学院学术活动
            'https://www.history.fudan.edu.cn/info/1062/1338.htm',  # 历史系讲座
            'https://philosophy.fudan.edu.cn/info/1049/1896.htm',  # 哲学学院讲座
            'https://www.math.fudan.edu.cn/1825/list.htm',  # 数学学院讲座
        ]
        
        for url in school_urls:
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                response.encoding = 'utf-8'
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 提取讲座信息
                lecture_items = soup.select('.wp_article_list li') + soup.select('.list_right li')
                for item in lecture_items:
                    try:
                        title = item.select_one('a').text.strip() if item.select_one('a') else item.text.strip()
                        # 筛选包含讲座关键词的条目
                        if any(keyword in title for keyword in ['讲座', '学术报告', '论坛', 'seminar', 'lecture']):
                            link = url.rsplit('/', 1)[0] + '/' + item.select_one('a')['href'] if item.select_one('a') and 'http' not in item.select_one('a')['href'] else item.select_one('a')['href']
                            date = item.select_one('.date').text.strip() if item.select_one('.date') else '未知'
                            
                            # 尝试从内容中提取时间和地点
                            location = '未知'
                            
                            # 添加到列表
                            self.lectures.append({
                                'title': title,
                                'date': date,
                                'location': location,
                                'source': 'Fudan School Website',
                                'link': link
                            })
                    except Exception as e:
                        print(f"处理学院网站讲座项时出错: {e}")
                
            except Exception as e:
                print(f"访问复旦大学学院网站 {url} 时出错: {e}")
                
            # 休眠一段时间
            time.sleep(self.get_random_sleep_time())
    
    def scrape_wechat_platform(self):
        """从微信平台抓取讲座信息"""
        # 注意：微信平台内容搜索需要调用API接口
        # 这里需要填写微信平台API接口信息
        
        # TODO: 微信平台API接口调用 - 需要手动补全
        # 以下是微信平台API调用的大致框架
        
        # 微信公众平台API需要申请开发者账号并获取相应的appid和secret
        WECHAT_APPID = os.getenv('WECHAT_APPID', '需要手动填写')
        WECHAT_SECRET = os.getenv('WECHAT_SECRET', '需要手动填写')
        
        # 微信搜索API - 可能需要第三方服务或自己开发爬虫
        # 这里是一个示例框架，实际实现需要根据具体API文档进行调整
        try:
            # 获取access_token
            # access_token_url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={WECHAT_APPID}&secret={WECHAT_SECRET}"
            # response = requests.get(access_token_url, timeout=10)
            # access_token = response.json().get('access_token')
            
            # 使用access_token调用相关API获取公众号文章
            # 注意：微信官方API并不直接提供搜索功能，可能需要使用第三方服务或自己开发爬虫
            
            # 以下是一些可能包含复旦大学讲座信息的公众号
            fudan_wechat_accounts = [
                '复旦招生',
                '复旦大学',
                '复旦研究生',
                '复旦大学学生会',
                '复旦学术',
                '复旦管院',
                '复旦就业'
            ]
            
            # 模拟微信平台抓取结果（实际需要API或爬虫支持）
            # 这里仅作为示例，实际实现需要替换为真实的API调用
            wechat_lectures = [
                {
                    'title': '【学术讲座】人工智能与未来社会发展',
                    'date': '2023-10-15',
                    'location': '复旦大学邯郸校区光华东楼100号',
                    'source': '复旦大学公众号',
                    'link': 'https://mp.weixin.qq.com/s/xxxxxxx'
                },
                {
                    'title': '【论坛】全球治理与中国方案',
                    'date': '2023-10-20',
                    'location': '复旦大学江湾校区会议中心',
                    'source': '复旦学术公众号',
                    'link': 'https://mp.weixin.qq.com/s/yyyyyyy'
                }
            ]
            
            # 将微信平台的讲座信息添加到总列表
            self.lectures.extend(wechat_lectures)
            
            print("微信平台数据抓取完成（模拟数据）")
            print("注意：实际应用中需要填写微信API接口信息并实现真实的API调用")
            
        except Exception as e:
            print(f"微信平台抓取出错: {e}")
            print("请检查微信API接口配置")
    
    def save_to_excel(self, filename='fudan_lectures.xlsx'):
        """将抓取的讲座信息保存到Excel文件"""
        if not self.lectures:
            print("没有抓取到任何讲座信息")
            return
        
        df = pd.DataFrame(self.lectures)
        # 按日期排序
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.sort_values(by='date', ascending=False)
        
        # 保存到Excel
        try:
            df.to_excel(filename, index=False)
            print(f"讲座信息已保存到 {filename}")
        except Exception as e:
            print(f"保存Excel文件时出错: {e}")
            # 尝试保存为CSV格式
            csv_filename = filename.replace('.xlsx', '.csv')
            df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
            print(f"讲座信息已保存到 {csv_filename}")
    
    def run(self):
        """运行整个抓取流程"""
        print("开始抓取复旦大学讲座信息...")
        
        # 从复旦大学官方网站抓取
        print("正在从复旦大学官方网站抓取讲座信息...")
        self.scrape_fudan_official()
        
        # 从各学院网站抓取
        print("正在从复旦大学各学院网站抓取讲座信息...")
        self.scrape_school_websites()
        
        # 从微信平台抓取
        print("正在从微信平台抓取讲座信息...")
        self.scrape_wechat_platform()
        
        # 去重
        if self.lectures:
            print(f"总共抓取到 {len(self.lectures)} 条讲座信息")
            # 简单去重（根据标题和链接）
            seen = set()
            unique_lectures = []
            for lecture in self.lectures:
                key = (lecture['title'], lecture['link'])
                if key not in seen:
                    seen.add(key)
                    unique_lectures.append(lecture)
            
            self.lectures = unique_lectures
            print(f"去重后剩余 {len(self.lectures)} 条讲座信息")
            
            # 保存到Excel
            self.save_to_excel(f"fudan_lectures_{datetime.now().strftime('%Y%m%d')}.xlsx")
        
        print("复旦大学讲座信息抓取完成")

if __name__ == "__main__":
    scraper = FudanLectureScraper()
    scraper.run()