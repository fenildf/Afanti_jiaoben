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
OUT_PATH = _DIR + '/outputfile/'
CONFIG_FILE = os.path.join(_DIR, 'config')
input_file = 'new_out_2.csv'
output_file = ''


def readCsvData():
    with open(INPUT_PATH + input_file, 'r', encoding='gbk') as raw_file:
        jobs = csv.DictReader(raw_file)
        for job in jobs:
            new_url = job['6']
            name = new_url.split('/')[-1]
            html = requests.get(new_url)
            with open(OUT_PATH + '/api_tag2/' + name, 'wb') as files:
                files.write(html.content)
                files.close()

def uplaodOss():
    OUTPUT_PATH = OUT_PATH + '/api_tag/'
    BUCKET_NAME = 'afanti-question-images'
    oss_path = 'data/api_tag/'

    oss_config['bucket_name'] = BUCKET_NAME
    oss_config['oss_path'] = oss_path
    OssFeng(
        config=oss_config,
        OUTPUT_PATH=OUTPUT_PATH,
    ).upload()


def removeOss():
    OUTPUT_PATH = OUT_PATH + '/api_tag/'
    BUCKET_NAME = 'afanti-question-images'
    oss_path = 'data/api_tag'

    oss_config['bucket_name'] = BUCKET_NAME
    oss_config['oss_path'] = oss_path
    OssFeng(
        config=oss_config,
        OUTPUT_PATH=OUTPUT_PATH,
    ).remove_one()


def newcsv():
    data = []
    with open(INPUT_PATH + input_file, 'r', encoding='gbk') as raw_file:
        jobs = csv.reader(raw_file)
        for job in jobs:
            job[5] = 'http://afanti-question-images.oss-cn-beijing.aliyuncs.com/data/api_tag/' + job[5].split('/')[-1]
            data.append(tuple(job))
        raw_file.close()
    data_pd = pd.DataFrame(data)
    data_pd.to_csv(OUT_PATH + input_file)



def gethtml(new_url):
    name = new_url.split('/')[-1]
    html = requests.get(new_url)
    with open(OUT_PATH + '/api_tag/' + name, 'wb') as files:
        files.write(html.content)
        files.close()


def renderPaper(root,f):
    cimage = BytesIO()
    im = Image.open(root + f)
    x, y = im.size
    p = Image.new('RGBA', im.size, (255, 255, 255))
    p.paste(im, (0, 0, x, y), im)

    p.save(os.path.join(root + f))




if __name__ == '__main__':
    # pool = Pool(4)
    # for root, dirs, files in os.walk(OUT_PATH + '/api_tag/'):
    #     for f in files:
    #         pool.apply_async(renderPaper, kwds={"root":root,"f":f})
    # pool.close()
    # pool.join()
    readCsvData()
    # uplaodOss()
    # removeOss()
    # newcsv()