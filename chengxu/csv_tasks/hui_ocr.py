# -*-coding:utf8-*-
import os
import sys
import json
import re
import urllib
import requests
import logging
import hashlib
import pymysql
import time
import csv
import random
import pandas as pd
from collections import OrderedDict
from multiprocessing import Pool
import platform
from io import BytesIO
from PIL import Image
from sogou_xml.spider_zdic.deallib.aliyun_oss_yinpin import OssFeng
from sogou_xml.spider_zdic.deallib.table_common import oss_config

_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))).replace('\\', '/')
INPUT_PATH = _DIR + '/inputfile/'
OUT_PATH = _DIR + '/outputfile/OCR/'
CONFIG_FILE = os.path.join(_DIR, 'config')
output_file = ''


def readCsvData(input_file):
    with open(INPUT_PATH + input_file, 'r', encoding='utf8') as raw_file:
        results = raw_file.readlines()
        raw_file.close()
    config = json.load(open(CONFIG_FILE))
    conn_3306 = pymysql.connect(host=config['host'], user=config['user'], passwd=config['password'],
                                db='question_pre', port=3306, charset="utf8",
                                use_unicode=True, cursorclass=pymysql.cursors.DictCursor)
    cur = conn_3306.cursor()
    file_path = inputfile.split('.')[0]
    path_jpg = OUT_PATH + file_path + '_jpg/'
    path_txt = OUT_PATH + file_path + '_txt/'
    if not os.path.exists(path_jpg):
        os.mkdir(path_jpg)
    if not os.path.exists(path_txt):
        os.mkdir(path_txt)
    for result in results[1:]:
        flag = 0
        txt_list = result.replace('\n', '').split('##')
        new_url = txt_list[0]
        name = new_url.split('/')[-1]
        try:
            html = requests.get(new_url)
            flag += 1
        except:
            flag = 0
        if flag == 1:
            sql = "select pure_text_question from question_search where spider_url = '{}'".format(txt_list[1])
            cur.execute(sql)
            data = cur.fetchall()
            if data:
                question_txt = data[0]['pure_text_question']
                flag += 1
            else:
                print(txt_list[1])
            if flag == 2:
                with open(path_jpg + name, 'wb') as files:
                    files.write(html.content)
                    files.close()
                with open(path_txt + name.split('.')[0] + '.txt', 'wt', encoding='gbk',errors='ignore') as file:
                    file.write(question_txt)
                    file.close()


if __name__ == '__main__':
    filename = ['chinese.txt','math.txt']
    filename = ['english.txt']
    for inputfile in filename:
        readCsvData(inputfile)
    print('as')