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
from jiaoben.Question.config import afanti,update2mysql

# LOGGING_FORMAT = '%(asctime)-15s:%(levelname)s: %(message)s'
# logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO,
#                                filename='working/baidu_idiom_bulou.log', filemode='a')

_DIR = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')


conn = pymysql.connect(host=afanti['host'], user=afanti['user'], passwd=afanti['password'],
                           db='tiku_cloud', port=afanti['port'], charset="utf8", use_unicode=True,
                           cursorclass=pymysql.cursors.DictCursor)


def get_data():
    '''
    填充ex_question的两个字段：question_type 和answer_all_html
    question_type: 1选择题  2填空题 3其他（具体规则：如果是选择题，question_html中有 class="aft_option" 字段；填空题有class="quizPutTag"> 字段）
    answer_all_html: 里面只填入选择题的正确答案选项，例如 ，A，具体规则需要看下解析字段.以上规则只针对 spider_source=3的题目，其他题目暂不管
    :return: 
    '''
    cur = conn.cursor()
    sql = "select * from ex_question where spider_source = 3"
    cur.execute(sql)
    datas = cur.fetchall()
    count_num = 0
    for data in datas:
        data_dict  = dict()

        question_type = data['question_type']
        question_type = 3
        option_html = data['option_html']
        if len(option_html) > 0:
            if 'class="aft_option"' in option_html:
                question_type = 1
        else:
            question_html = data['question_html'].strip()
            if 'class="quizPutTag"' in question_html:
                question_type = 2
            elif 'class="aft_option"' in question_html:
                question_type = 1

        data_dict['question_type'] = question_type

        answer_all_html = data['answer_all_html']
        if len(answer_all_html) == 0 and question_type == 1 and len(data['jieda']):
            # count_num += 1
            jiada= data['jieda'][-3:].upper()
            xuan = ['A','B','C','D']
            i = 0

            a = ''
            while i < 4:
                if xuan[i] in jiada:
                    data_dict['answer_all_html'] = xuan[i]
                    break
                i += 1
            if len(data_dict.get('answer_all_html','')) == 0:
                jieda_p = re.findall('故选(.+?)．', data['jieda'])
                if jieda_p:
                    jieda_str = jieda_p[0].replace('：','').replace('','').strip()
                    if len(jieda_str) == 1:
                        if jieda_str.isdigit():
                            jieda_str = chr(int(jieda_str) + 64)
                        data_dict['answer_all_html'] = jieda_str.upper()
                    else:
                        print(jieda_p)
                else:
                    print(data['jieda'])

        id = data['question_id']
        where = "where question_id = {}".format(id)
        update2mysql(conn, "ex_question", where, data_dict)


if __name__ == '__main__':
    get_data()

