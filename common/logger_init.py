# -*- coding: utf-8 -*-
# @Time    : 2020/2/25 14:13 
# @Author  : zbs
# @Site    :
# @File    : logger_init.py
# @Software: PyCharm
import logging

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler("log.txt", 'w')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)