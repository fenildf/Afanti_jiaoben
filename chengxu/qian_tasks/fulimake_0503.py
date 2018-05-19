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
import random
from collections import OrderedDict
from jiaoben.Question.config import afanti,update2mysql,get_conn,data2mysql,get_md5

LOGGING_FORMAT = '%(asctime)-15s:%(levelname)s: %(message)s'
logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO,
                               filename='working/fulimake_0503_02.log', filemode='a')

_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))).replace('\\', '/')
INPUT_PATH = _DIR + '/inputfile/'
conn_db_off = get_conn(afanti, "question_db_offline")
conn_pre = get_conn(afanti, "question_pre")
afanti['host'] = '172.16.16.10'
conn_pre_write = get_conn(afanti, "question_pre")
jiance_list = ['jingyou', 'jye', 'jy', '菁优']


def set_flag(dt):
    flag = 1
    jiance = ''
    i = 0
    while i < 4:
        if jiance_list[i] in dt['question_html'] or jiance_list[i] in dt['option_html'] or jiance_list[
            i] in dt['answer_all_html'] or jiance_list[i] in dt['jieda'] or jiance_list[
            i] in dt['fenxi'] or jiance_list[i] in dt['dianping']:

            flag = 0
            jiance = jiance_list[i]
            break

        i += 1
    return flag, jiance


def get_spiderurl():
    cur = conn_pre.cursor()
    # 'wangsq.result'
    with open(INPUT_PATH + '3500.result', 'r', encoding='utf8') as file:
        while True:
            result = file.readline().replace('\n', '')
            if not result:
                break

            question_id = result.split('\t')[1]
            sql = "select spider_url from question where question_id = '{}'".format(question_id)
            cur.execute(sql)
            data = cur.fetchall()

            if data:
                spider_url = data[0]['spider_url']
                with open(INPUT_PATH + '3500_spiderurl.result','a',encoding='utf8') as new_file:
                    new_file.write(spider_url + '\n')


def dealimage(html):
    if '<img src="http:' in html:
        html = html.replace('://img.afanti100.com/', '://qimg.afanti100.com/')
        image_p = re.findall('<img src="(.+?)"', html, re.S|re.I)
        if image_p:
            for im in image_p:
                im_p = re.findall('png(.+)', im)
                if im_p:
                    for i in im_p:
                        html = html.replace(i, '')

    return html


def insert_fulimake():
    ziduan_dict = {
        'timu':'question_html',
        'xuanxiang':'option_html',
        'daan':'answer_all_html',
        'jieda':'jieda',
        'fenxi':'fenxi',
        'dianping':'dianping'
    }
    cur = conn_db_off.cursor()
    with open(INPUT_PATH + '3500_spiderurl.result', 'r', encoding='utf8') as file:
        while True:
            result = file.readline().replace('\n','')
            if not result:
                break

            spider_url = result
            sql = "select * from jyeoo_app_question_20160926 where spider_url = '{}'".format(spider_url)
            cur.execute(sql)
            data = cur.fetchall()

            if data:
                data_dict = dict()
                dt = data[0]
                flag, jiance = set_flag(dt)
                if flag == 1:
                    data_dict['qid'] = get_md5(spider_url)
                    data_dict['zhishidian'] = dt['knowledge_point']
                    data_dict['xueke'] = dt['subject']
                    for key,value in ziduan_dict.items():
                        data_dict[key] = dealimage(dt[value])
                    data2mysql(conn_pre_write, data_dict, "fulimake_all")
                else:
                    with open('working/spider_url_jiance.txt', 'a', encoding='utf8') as f:
                        f.write(spider_url + '\t' + jiance + '\n')
                    # logging.error("{0} 出现非法字段 {1}".format(spider_url, jiance))

            else:
                logging.error("{} 在jyeoo_app_question_20160926表中没有找到数据".format(spider_url))


if __name__ == '__main__':
    get_spiderurl()
    insert_fulimake()
    print('as')