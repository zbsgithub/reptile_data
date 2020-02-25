# -*- coding: utf-8 -*-
# @Time    : 2020/2/25 13:49 
# @Author  : zbs
# @Site    :
# @File    : reptile_main.py
# @Software: PyCharm

import schedule
import time
import re
import datetime
import pymongo
from bs4 import BeautifulSoup
import requests
import traceback
import json
import sys
from common.logger_init import logger


class Reptile():

    def __init__(self, mongodb_address, mongodb_port, net_addr):
        self.mongodb_address = mongodb_address
        self.mongodb_port = mongodb_port
        self.net_addr = net_addr

    def handle_task(self):

        logger.info('----task handle begin time:%s' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        self.sov_html()
        logger.info('----task handle end time:%s' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    def mongodb(self, total_page, total_count):
        try:
            cl = pymongo.MongoClient(self.mongodb_address, self.mongodb_port)
            # client = pymongo.MongoClient('mongodb://localhost:27017/')
            db = cl['dev']
            collection = db['tzgg']

            collec_size = collection.count()
            current_time = time.strftime('%Y-%m-%d', time.localtime())
            logger.info("库中总记录数：%d" % collec_size)
            if int(total_count) == collec_size:
                logger.info( '----------------------database data aleardy new -----------%s---------------' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            else:
                logger.info('------------------------------------database data begin syn --------------------------')
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

                        logger.info("第%s页 %s   %s  %s" % (str(page), title, pub_time, content_address))

                        insert_data = {
                            'title': title,
                            'publish_time': pub_time,
                            # 'content': content,
                            'creat_time': current_time
                        }
                        collection.insert(insert_data)

                logger.info('------------------------------------database data begin syn --------------------------')
        except:
            traceback.format_exc()

    def sov_html(self):
        target = self.net_addr
        bf = self.gener_sov_html(target)
        texts = bf.find_all(id='fanye253250')[0].string
        total_page = texts.replace(" ", "").split("条")[1].split("/")[1]

        regex = r'共([\s\S]*)条'
        total_recoard_count = re.findall(regex, texts)
        total_count = total_recoard_count[0]

        self.mongodb(total_page, total_count)

    def gener_sov_html(self, address):
        req = requests.get(url=address)
        html = req.content.decode('utf-8')
        bf = BeautifulSoup(html, "lxml")

        return bf

    def run(self):
        schedule.every(2).minutes.do(self.handle_task)
        # schedule.every(2).hour.do(self.handle_task)
        while True:
            schedule.run_pending()


if __name__ == '__main__':
    config_file = sys.argv[1]
    with open(config_file, 'r', encoding='utf-8') as file:
        config = json.load(file)

    reptile = Reptile(config["mongodb"]["address"], config["mongodb"]["port"], config["net_address"])
    reptile.run()
