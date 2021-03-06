# Author: Chenchen
import pandas as pd
import requests
from lxml import etree
import re
import json
import datetime
import queue
from multiprocessing.dummy import Pool
class WebOfScience(object):
# if True:
    sess=requests.Session()
    sid="6DDMrlnZtB8Hz6wEwOW"
    url_detail="http://ifbic9558b67dd89e4aa8svonnbfbwbcnb60qc.fiac.eds.tju.edu.cn/UA_GeneralSearch.do"
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36",
    }
    data=[
    ("action", "search"),
    ("product", "UA"),
    ("search_mode","GeneralSearch"),
    ("SID",sid),
    ("max_field_count","25"),
    ("sa_params", "UA||6DDMrlnZtB8Hz6wEwOW|http://ifbicd9871f8a00174050svonnbfbwbcnb60qc.fiac.eds.tju.edu.cn|"),
    ("formUpdated","true"),
    ("limitStatus", "expanded"),
    ("ss_lemmatization", "On"),
    ("ss_spellchecking", "Suggest"),
    ("SinceLastVisit_UTC",""),
    ("SinceLastVisit_DATE",""),
    ("period", "Range Selection"),
    ("range", "ALL"),
    ("editions", "WOS.ESCI"),
    ("editions","WOS.SSCI"),
    ("editions", "WOS.SCI"),
    ("editions", "WOS.IC"),
    ("editions", "WOS.AHCI"),
    ("editions", "WOS.ISTP"),
    ("editions", "WOS.CCR"),
    ("collections", "WOS"),
    ("editions", "CSCD.CSCD"),
    ("collections", "CSCD"),
    ("editions", "DIIDW.EDerwent"),
    ("editions", "DIIDW.CDerwent"),
    ("editions", "DIIDW.MDerwent"),
    ("collections", "DIIDW"),
    ("editions", "KJD.KJD"),
    ("collections", "KJD"),
    ("editions", "MEDLINE.MEDLINE"),
    ("collections", "MEDLINE"),
    ("editions", "RSCI.RSCI"),
    ("collections", "RSCI"),
    ("editions", "SCIELO.SCIELO"),
    ("collections", "SCIELO"),
    ("update_back2search_link_param", "yes"),
    ("ssStatus", "display:none"),
    ("ss_showsuggestions", "ON"),
    ("ss_query_language", "auto"),
    ("ss_numDefaultGeneralSearchFields","1"),
    ("rs_sort_by", "PY.D;LD.D;SO.A;VL.D;PG.A;AU.A"),
    ]
    def __init__(self,field):
        self.key_data=field
        self.qid=None
        self.result_list=[]
        self.total_page_counts=None
        self.result_counts=None
    def get_detail(self):
        self.data.extend(self.key_data)
        response=requests.post(self.url_detail,data=self.data,headers=self.headers)
        tree=etree.HTML(response.text)
        self.result_counts=tree.xpath("//*[@id='trueFinalResultCount']/text()")[0]   #????????????????????????
        total_page_counts=tree.xpath('//*[@id="pageCount.top"]/text()')[0]      #??????????????????
        if "," in total_page_counts:
            self.total_page_counts="".join(total_page_counts.split(","))
        else:
            self.total_page_counts=total_page_counts
        value_contain_qid=tree.xpath('//*[@id="currUrl"]/@value')[0]
        pid_pattern=re.compile("qid=(\d+)")
        self.qid=pid_pattern.search(value_contain_qid).group(1)
        print(f"????????????????????????:{self.result_counts},???{self.total_page_counts}??????qid={self.qid}")

    def get_page(self,page_num):
        url_page="http://ifbicd9871f8a00174050svonnbfbwbcnb60qc.fiac.eds.tju.edu.cn/summary.do"
        # for page in range(1,int(total_page_counts)+1):
        all_ls=[]
        params={
            "product": "UA",
            "parentProduct": "UA",
            "search_mode": "GeneralSearch",
            "parentQid":"",
            "qid":self.qid,
            "SID": self.sid,
            "update_back2search_link_param": "yes",
            "page": page_num,
        }
        response=self.sess.get(url_page,headers=self.headers,params=params)
        return response

        # page_detail.encoding="utf-8"


    def parse_page_detail(self,response,page_num):
        detail_tree=etree.HTML(response.text)
        # with open("detail.html","w",encoding='utf-8')as fp:
        #     fp.write(response.text)
        research_results=detail_tree.xpath("//div[@class='search-results']/div")
        page_ls= []
        count=1
        flag=True
        # try:
        if True:
            for record_num in research_results:    #???????????????????????????
                try:
                    title="".join(record_num.xpath('./div[3]/div/div[1]//text()')).replace("\n","").replace("\xa0"," ").replace("\u200f","")
                    # print(title)
                    author="".join(record_num.xpath('./div[3]/div/div[2]/a//text()')).replace("\n",";").replace("\xa0"," ").replace("\u200f","")
                    journal_msg=record_num.xpath('./div[3]/div/div[3]//value')
                    journal_name=journal_msg[0].xpath("./text()")[0]
                    volume=journal_msg[1].xpath("./text()")[0]
                    issue=journal_msg[2].xpath("./text()")[0]
                    pages=journal_msg[3].xpath("./text()")[0]
                    if len(journal_msg)==6:
                        published_year=journal_msg[5].xpath("./text()")[0]
                    else:
                        try:
                            published_year = journal_msg[4].xpath("./text()")[0]
                        except Exception as e:
                            published_year=None
                    count+=1
                except Exception as e:
                    print(f"???{page_num}??????{count}??????????????????")
                    flag=False
                    continue
                page_ls.append({"Title":title,"Author":author,"Volume":volume,"Issue":issue,"Pages":pages,"Journal":journal_name,"Published_year":published_year})
            if flag:
                print(f"???{page_num}??????????????????")
        # except Exception as e:

        return page_ls

    def get_page_detail(self,page_num):
        response=self.get_page(page_num)
        return self.parse_page_detail(response,page_num)
    def download(self,*args):
        pool = Pool(15)
        tem_ls=[]
        start=1
        end=int(self.total_page_counts)+1
        args=list(map(lambda x:int(x),args))
        if len(args)==1:
            end=args[0]+1
        elif len(args)==2:
            start=args[0]
            end=args[1]+1
        while end-start>20:
            tem_ls.extend(pool.map(self.get_page_detail,list(range(start,start+20))))
            start+=20
        else:
            tem_ls.extend(pool.map(self.get_page_detail,list(range(start,end))))
        tem=[]
        for page in tem_ls:
            tem.extend(page)
        self.result_list=tem

# def get_year():
#         start="1950"
#         end=str(datetime.date.today()).split("-")[0]
#         while True:
#             choice=input("??????????????????(y|n)?>>")
#             if choice=="y":
#                 year=input("??????????????????,???????????????????????????(??????:1994,2019)>>").strip()
#                 if year:
#                     start_=year.split(",")[0]
#                     end_=year.split(",")[1]
#                     start=start_ if start_ else start
#                     end=end_ if end_ else end
#                     break
#                 else:
#                     continue
#             elif choice=="n":
#                 break
#             else:
#                 print("????????????!")
#         return (start,end)
# def get_field():
#     operate_dic = {
#         "??????": "TS",
#         "??????": "TI",
#         "??????": "AU",
#         "???????????????": "SO",
#         "??????": "AD",
#         "???????????????": "AI",
#     }
#     print("?????????????????????:", list(operate_dic.keys()))
#     print("??????:")
#     flag = True
#     pattern = re.compile("(end)")
#     field = ""
#     while flag:
#         choice_field = input("???????????????????????????,??????'end'????????????:") + ","
#         field += choice_field
#         if pattern.search(field):
#             break
#     print(field)
def main(field):
    web = WebOfScience(field)
    web.get_detail()
    choice=input("?????????????(y|n)>>")
    while True:
        if choice=="y":
            page=input("?????????????????????>>").strip()
            if ","in page:
                page=page.split(",")
                web.download(*page)
            elif not len(page):
                web.download("1",web.total_page_counts)
            else:
                web.download(page)
            break
        elif choice=="n":
            break
        else:
            print("????????????~")
            choice = input("?????????????(y|n)>>")
            continue
    result=web.result_list
    df=pd.DataFrame(result)
    df["Published_year"]=df["Published_year"].str.extract("(\d+$)")
    df.to_excel("????????????.xlsx",index=False)

if __name__=="__main__":
    '''
        ??????????????????
            "??????": "TS",
            "??????": "TI",
            "??????": "AU",
            "???????????????": "SO",
            "??????": "AD",
            "???????????????": "AI",
        ??????????????????AND,OR,NOT
        ?????????
            field=[
                    ("fieldCount", "1"),
                    ("value(input1)", "DFT study"),
                    ("value(select1)", "TS"),
                    ("value(bool_1_2)": "AND")
                    ("value(input2)", "chen hai"),
                    ("value(select3)", "AU"),
                    ("startYear", "1950"),
                    ("endYear", "2021"),
            ]
        '''
    field = [
        ("fieldCount", "2"),
        ("value(input1)", "yu yingzhe"),
        ("value(select1)", "AU"),
        ("value(bool_1_2)","AND"),
        ("value(input2)", "Tianjin University"),
        ("value(select2)", "AD"),
        ("startYear", "1950"),
        ("endYear", "2021"),
    ]
    main(field)


