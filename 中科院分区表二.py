# Author: Chenchen
import requests
from selenium import webdriver
from lxml import etree
import time
import re
from multiprocessing.dummy import Pool
# import numpy as np
# import pandas as pd
class JCRQery(object):
    sess = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36",
        # "Host":" ifyhif15fa195ed6742f6h9on0kp0nfknb6qvk.fbyy.eds.tju.edu.cn",
        # "Referer":" http: // ifyhif15fa195ed6742f6h9on0kp0nfknb6qvk.fbyy.eds.tju.edu.cn / Core / Search.aspx",
        "Upgrade - Insecure - Requests": "1"
    }
    # chrome_options=webdriver.ChromeOptions()
    # chrome_options.add_argument('--proxy-server=https://222.37.120.206:46603')
    bro = webdriver.Chrome()
    all_ip=[
        {"https":"222.37.120.206:46603"},
        {"https":"125.78.218.215:25400"},
    ]
    # index_url = "http://ifyhif15fa195ed6742f6huwnocxvoqvx965vb.fbyy.eds.tju.edu.cn/"
    def __init__(self,url,journal_list):
        self.url=url
        self.journal_list=journal_list
        self.token=self.get_token()
        self.login=self.login()
        # self.ip_api=None
    # def ip_pool(self):
    #     all_ip=[]
        # response=requests.get(self.ip_api).text
        # tree=etree.HTML(response)
        # tree.xpath("//body/text()")
    def get_token(self):
        self.bro.get(self.url)
        time.sleep(1)
        tree = etree.HTML(self.bro.page_source)
        token = tree.xpath('//*[@id="token"]/@value')
        with open("../test.html", "w", encoding="utf-8")as p:
            p.write(self.bro.page_source)
        self.bro.quit()
        if token:
            return token[0]
        else:
            print("token获取失败！")
            return False

    def login(self):
        # response1 = self.sess.get(self.url, headers=self.headers)
        if self.token:
            data = {
                "user": "tju",
                "pwd": "tju",
                "g-recaptcha-response": self.token,
            }
            post_url = self.url + "Default.aspx"
            #模拟登录
            response=self.sess.post(post_url, headers=self.headers, data=data)
            with open("分区表.html", "w", encoding="utf-8")as fp:
                fp.write(response.text)
            if response.status_code==200:
                return True

    def assign(self):
        pool=Pool(len(self.journal_list))
        return pool.map(self.get_detail_dict,self.journal_list)
        # return map(self.get_detail_dict,self.journal_list)
    def get_detail_dict(self,journal):
        pattern=re.compile("\d")
        y=journal[1]
        t=journal[0]
        detail_url = self.url +"Core/JournalDetail.aspx?"
        params = {
            "y":y,
            "t":t,
        }
        response = self.sess.get(detail_url, headers=self.headers,params=params)
        response.encoding = "utf-8"
        detail_tree = etree.HTML(response.text)
        with open("分区表.html", "w", encoding="utf-8")as fp:
            fp.write(response.text)
        # if True:
        try:
            dic = {
                "期刊全称": detail_tree.xpath('//*[@id="detailJournal"]/tbody/tr[1]/td[2]/text()')[0],
                "期刊简称": detail_tree.xpath('//*[@id="detailJournal"]/tbody/tr[2]/td[2]/text()')[0],
                "ISSN": detail_tree.xpath('//*[@id="detailJournal"]/tbody/tr[2]/td[4]/text()')[0],
                "年份": detail_tree.xpath('//*[@id="detailJournal"]/tbody/tr[3]/td[2]/text()')[0],
                "大类": detail_tree.xpath('//*[@id="categorylist"]/tbody/tr[last()]/td[2]/text()')[0],
                "分区":pattern.search(detail_tree.xpath('//*[@id="categorylist"]/tbody/tr[last()]/td[3]/text()')[0]).group(),
                "Top期刊": detail_tree.xpath('//*[@id="categorylist"]/tbody/tr[last()]/td[4]/text()')[0],
            }
        except Exception as e:
            print("没有正常请求到详情页信息，请检查请求是否正确",f"错误信息:{e}")
        else:
            year_tags = detail_tree.xpath('//*[@id="impactfactorlist"]/tbody/tr[2]/td')[0:4]
            IF_tags = detail_tree.xpath('//*[@id="impactfactorlist"]/tbody/tr[3]/td')[0:4]
            def map_func(dic, li1, li2):
                """
                用来映射影响因子年份和对应的影响因子，并添加到字典中
                :param dic:
                :param li1: year_tags [["a",],]
                :param li2: year_tags [["a",],]
                :return:
                """

                def element_to_str(li):
                    tem = []
                    for i in li:
                        tem.append(i.xpath("./text()")[0])
                    return tem

                li1 = element_to_str(li1)
                li2 = element_to_str(li2)
                for i in range(len(li1)):
                    dic[li1[i]+"IF"] = li2[i]
                return dic

            dic = map_func(dic, year_tags, IF_tags)
            return dic

    def query(self):
        if self.login:
            return self.assign()
        else:
            return "登录失败！"
if __name__=="__main__":
    url="http://hfyhif15fa195ed6742f6hkqwvkv0wxwf56ovq.fbyy.eds.tju.edu.cn/"
    # tem_list=[("applied surface science","2014"),("nature","2019"),("Molecular Catalysis","2020")]
    tem_list=[]
    for i in range(2019,2020):
        tem_list.append(("applied surface science",f"{i}"))
    jcr=JCRQery(url,tem_list)
    res_list=jcr.query()
    for i in res_list:
        print(i)
    print(len(list(res_list)))



# response3=sess.get(index_url+"Core/Search.aspx")
# response3.encoding="utf-8"

