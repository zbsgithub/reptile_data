# -*- coding: utf-8 -*-
# @Time    : 2020/2/25 15:36 
# @Author  : zbs
# @Site    :
# @File    : syn_data.py
# @Software: PyCharm

import schedule
import time
import re
import datetime
import pymongo
from bs4 import BeautifulSoup
import requests
import traceback
import logging
import pymysql
from urllib import parse


class Reptile():

    def __init__(self, mongodb_address, mongodb_port, net_addr):
        self.mongodb_address = mongodb_address
        self.mongodb_port = mongodb_port
        self.net_addr = net_addr

    def handle_task(self):

        logging.info('----task handle begin time:%s' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        self.sov_html()
        logging.info('----task handle end time:%s' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    def mongodb(self, total_page, total_count):
        try:
            cl = pymongo.MongoClient(self.mongodb_address, self.mongodb_port)
            # client = pymongo.MongoClient('mongodb://localhost:27017/')
            db = cl['dev']
            collection = db['tzgg']

            collec_size = collection.count()
            current_time = time.strftime('%Y-%m-%d', time.localtime())
            logging.info("库中总记录数：%d" % collec_size)
            if int(total_count) == collec_size:
                logging.info(
                    '----------------------database data aleardy new -----------%s---------------' % datetime.datetime.now().strftime(
                        '%Y-%m-%d %H:%M:%S'))
            else:
                logging.info('------------------------------------database data begin syn --------------------------')
                collection.remove()
                for page in range(int(total_page)):
                    if page == 0:
                        target = self.net_addr
                    else:
                        target = 'http://www.hbun.edu.cn/wzdh/tzgg/' + str(page) + '.htm'

                    bf = self.gener_sov_html(target)
                    for i in bf.select('div.list_box li'):
                        title = i.find("a").get_text()
                        pub_time = i.find("span").get_text()
                        content_address = i.find("a")["href"].split("../")[1]

                        # content_bf = gener_sov_html("http://www.hbun.edu.cn/" + content_address)
                        # content = content_bf.find_all("div", class_="v_news_content")

                        logging.info("第%s页 %s   %s  %s" % (str(page), title, pub_time, content_address))

                        insert_data = {
                            'title': title,
                            'publish_time': pub_time,
                            # 'content': content,
                            'creat_time': current_time
                        }
                        collection.insert(insert_data)

                logging.info('------------------------------------database data begin syn --------------------------')
        except:
            traceback.format_exc()

    def sov_html(self):
        target = self.net_addr
        bf = self.gener_sov_html(target)
        texts = bf.find_all(id='fanye253250')[0].string
        for province in bf.select("tbody.provincetr td"):
            provinceStr = province.find("a").get_text().split("<br/>")[0]
            logging.info("省：{}", provinceStr)

    def gener_sov_html(self, address):
        req = requests.get(url=address)
        html = req.content.decode('GB18030', 'ignore')
        bf = BeautifulSoup(html, "html.parser")

        return bf

    def run(self):
        target = self.net_addr
        bf = self.gener_sov_html(target)
        base_req_address = "http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2020/"

        #遍历省
        for province in bf.select("table.provincetable tr a"):
            # 打开数据库连接，不指定数据库
            conn = pymysql.connect('root_1234', 'Cctv1234!', 'rm-2ze9nq48u5k59ea513o.mysql.rds.aliyuncs.com')
            conn.select_db('base_area')
            logging.info("connect database is success !")
            cur = conn.cursor()  # 获取游标

            province_address = province.get("href")
            logging.info(province.get_text()) #省名称
            logging.info(province_address.split(".")[0])

            #遍历市
            city_html_address_pre = base_req_address + province_address
            # logging.info("省：{}  address：{}",province.get_text(),city_html_address_pre)

            bf_city = self.gener_sov_html(city_html_address_pre)
            for city in bf_city.select("tbody tr.citytr"):
                logging.info(city.find_all("td")[1].get_text())#市名称
                # logging.info(city.select("td")[0].find("a").get("href"))

                #遍历区
                area_html_address_pre = base_req_address + city.select("td")[0].find("a").get("href")
                # logging.info(area_html_address_pre)
                bf_area = self.gener_sov_html(area_html_address_pre)
                for area in bf_area.select("tbody tr.countytr"):
                    logging.info(area.find_all("td")[1].get_text())  # 区名称
                    # logging.info(area.select("td")[0].find("a"))

                    # 遍历街道
                    if area.select("td")[0].find("a") != None:
                        street_html_address_pre = base_req_address + province_address.split(".")[0] + "/" + area.select("td")[0].find("a").get("href")
                        # logging.info(street_html_address_pre)

                        bf_street = self.gener_sov_html(street_html_address_pre)
                        for street in bf_street.select("tbody tr.towntr"):
                            logging.info(street.find_all("td")[1].get_text())  # 街道地址
                            # logging.info(street.select("td")[0].find("a"))

                            # 另一种插入数据的方式，通过字符串传入值
                            sql = "insert into street (street_name,region,city,province) values ('%s','%s','%s','%s')" % (street.find_all("td")[1].get_text(), area.find_all("td")[1].get_text(), city.find_all("td")[1].get_text(), province.get_text())
                            cur.execute(sql)
            cur.close()
            conn.commit()
            conn.close()
        logging.info("------------------------------program excute is over--------------------------------")





