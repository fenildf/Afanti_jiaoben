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
from w3lib.html import remove_tags
from snownlp import SnowNLP
from jiaoben.Question.config import afanti,update2mysql,get_conn,data2mysql,get_md5

# LOGGING_FORMAT = '%(asctime)-15s:%(levelname)s: %(message)s'
# logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO,
#                                filename='working/fulimake_0503_02.log', filemode='a')

_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))).replace('\\', '/')
INPUT_PATH = _DIR + '/inputfile/'
conn_pre = get_conn(afanti, "question_pre")

def dealSummaryText(summary_p):
    i = 0
    l = len(summary_p)
    summ = ''
    while i < l:
        summb = remove_tags(summary_p[i]).strip().encode('utf8')
        i += 1
        if b'\x1f' not in summb and b'\x04\x03' not in summb:
            summ = summb.decode('utf8')
            break

    if l == 1:
        return summ

    while len(summ) < 10 and i < l:
        summ += remove_tags(summary_p[i]).strip()
        i += 1

    spliter = ['。', '，', '．', ',', '-']
    if len(summ.encode('utf8')) > 1000:
        for sp in spliter:
            while len(summ.encode('utf8')) > 1000:
                if not sp in summ:
                    break
                pos = summ.rfind(sp)
                summ = summ[:pos]
            if len(summ.encode('utf-8')) <= 1000:
                break

    if summ[-1] in spliter[1:]:
        summ = summ[:-1]

    return summ


def updateSummaryText():
    cur = conn_pre.cursor()
    yuzhi = 0
    while True:
        sql = "select spider_url,`text` from chinese_essay_sogou limit {},10000".format(yuzhi)
        # sql = "select spider_url,`text` from chinese_essay_sogou where summary like '%白白，白白最喜欢吃青菜和料，因为养料太贵，所以就买青菜给白白吃，就这样，爸爸每天用5角钱买青菜%'"
        cur.execute(sql)
        datas = cur.fetchall()
        if not datas:
            break

        yuzhi += 10000

        for data in datas:
            text = data['text']
            summary_p = re.findall('<p>(.+?)</p>', text, re.S|re.I)
            if summary_p:
                summary = dealSummaryText(summary_p)
                where = "where spider_url = '{}'".format(data['spider_url'])
                update2mysql(conn_pre,"chinese_essay_sogou",where,{"summary":summary})


def dealSummaryNLP(text):
    s = SnowNLP(text)
    i = 5
    while i > 0:
        summary = '，'.join(s.summary(i)) + '。'
        if len(summary.encode('utf8')) < 1000:
            break
        i -= 1
    return summary


def updateSummaryNLP():
    cur = conn_pre.cursor()
    yuzhi = 0
    while True:
        sql = "select spider_url,`pure_text` from chinese_essay_sogou limit {},10000".format(yuzhi)
        cur.execute(sql)
        datas = cur.fetchall()
        if not datas:
            break

        yuzhi += 10000

        for data in datas:
            text = data['pure_text']
            summary = dealSummaryNLP(text)
            where = "where spider_url = '{}'".format(data['spider_url'])
            # update2mysql(conn_pre,"chinese_essay_sogou",where,{"summary":summary})


if __name__ == '__main__':
    updateSummaryText()
    # updateSummaryNLP()
    print('ad')
