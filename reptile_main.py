# -*- coding: utf-8 -*-
# @Time    : 2020/2/25 13:49 
# @Author  : zbs
# @Site    :
# @File    : reptile_main.py
# @Software: PyCharm

import sys
import json
import os
# from common.syn_data import Reptile
from common.syn_tjj import Reptile
from utils.log import log_init

if __name__ == '__main__':
    config_file = sys.argv[1]
    with open(config_file, 'r', encoding='utf-8') as file:
        config = json.load(file)

    project_dir = os.path.abspath(__file__)
    config['logging']['path'] = os.path.join(os.path.dirname(project_dir), config['logging']['path'])
    log_init(config['logging'])

    reptile = Reptile(config["mongodb"]["address"], config["mongodb"]["port"], config["net_address"])
    reptile.run()
