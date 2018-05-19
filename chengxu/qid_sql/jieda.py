# -*-coding:utf8-*-
import os
import sys
import json
import logging
import pymysql
import pymysql.cursors
from tiku_lib.text import get_latex_text_for_search

LOGGING_FORMAT = '%(asctime)-15s:%(levelname)s: %(message)s'
logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO,
                                filename='working/jieda.log', filemode='a')

_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))).replace('\\', '/')
INPUT_PATH = _DIR + '/inputfile/'
OUT_PATH = _DIR + '/outputfile/'
CONFIG_FILE = os.path.join(_DIR, 'config')
# input_file = '111.qid'
# input_file = '2000_all.qid'
# output_file = '777.txt'
input_file = '8881.qid'
output_file = '999.txt'

def secondTable(spider_url, result):
    #采用同步的机制写入mysql
    config = json.load(open(CONFIG_FILE))
    conn = pymysql.connect(host=config['host'], user=config['user'], passwd=config['password'], db='question_db_offline',
                           port=3306, charset= "utf8", use_unicode=True, cursorclass = pymysql.cursors.DictCursor)
    cursor = conn.cursor()

    sql1 = "select jieda_origin from {0} WHERE spider_url = '{1}' ".format('jyeoo_app_question_20160926', spider_url)
    sql2 = "select jieda_origin from {0} WHERE spider_url = '{1}' ".format('jyeoo_20160720', spider_url)
    cursor.execute(sql1)
    data = cursor.fetchall()

    if len(data) > 0:
        data1 = data[0]
        jieda = get_latex_text_for_search(data1['jieda_origin'])
        if "}_{" in jieda or "}^{" in jieda :
            if "frac" not in jieda and "begin" not in jieda:
                if '\n' not in jieda:
                    with open(OUT_PATH + output_file, 'a', encoding='utf-8') as ot_file:
                        ot_file.write(result + '\t' + jieda + '\n')
                else:
                    with open(OUT_PATH + output_file, 'a', encoding='utf-8') as ot_file:
                        ot_file.write(result + '\t' + jieda)

    else:
        cursor.execute(sql2)
        data2 = cursor.fetchall()
        if len(data2) > 0:
            data2 = data2[0]
            jieda = get_latex_text_for_search(data2['jieda_origin'])
            if "}_{" in jieda or "}^{" in jieda:
                if "frac" not in jieda and "begin" not in jieda:
                    if '\n' not in jieda:
                        with open(OUT_PATH + output_file, 'a', encoding='utf-8') as ot_file:
                            ot_file.write(result + '\t' + jieda + '\n')
                    else:
                        with open(OUT_PATH + output_file, 'a', encoding='utf-8') as ot_file:
                            ot_file.write(result + '\t' + jieda)


def tableToJson(table, result):
    config = json.load(open(CONFIG_FILE))
    conn = pymysql.connect(host=config['host'], user=config['user'], passwd=config['password'], db='question_pre',
                           port=3306, charset= "utf8", use_unicode=True, cursorclass = pymysql.cursors.DictCursor)
    cur = conn.cursor()
    sql = "select spider_url from {0} WHERE question_id = '{1}' ".format(table, result)


    cur.execute(sql)
    data = cur.fetchall()

    if len(data) > 0:
        data = data[0]
        spider_url = data['spider_url']
        secondTable(spider_url, result)

    else:
        logging.error("解读到{0}时，没有相应question_id".format(result))


def readTxt():
    with open(INPUT_PATH + input_file, 'r', encoding='utf-8') as txt_file:
        while True:
            line = txt_file.readline()
            if line:
                result = line.replace('\n','')
                tableToJson(
                    table='question',
                    result=result
                )

            else:
                break
        txt_file.close()



if __name__ == '__main__':
    if os.path.exists(output_file):
        os.remove(output_file)
    readTxt()