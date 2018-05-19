# -*-coding:utf8-*-
import os
import sys
import json
import logging
import pymysql
import pymysql.cursors
from tiku_lib.text import get_pure_text_for_search

LOGGING_FORMAT = '%(asctime)-15s:%(levelname)s: %(message)s'
logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO,
                                filename='working/question_count.log', filemode='a')

_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))).replace('\\', '/')
INPUT_PATH = _DIR + '/inputfile/'
CONFIG_FILE = os.path.join(_DIR, 'config')
input_file = 'question.txt'

def Data_to_MySQL(datas):
    #采用同步的机制写入mysql
    config = json.load(open(CONFIG_FILE))
    conn = pymysql.connect(host=config['host'], user=config['user'], passwd=config['password'], db='question_pre',
                           port=3306, charset= "utf8", use_unicode=True, cursorclass = pymysql.cursors.DictCursor)
    cursor = conn.cursor()

    cols, values = zip(*datas.items())

    insert_sql = 'insert ignore into {table} ({cols}) values ({values})'.format(
        table='txt_question_20171213',
        cols=', '.join(['`%s`' % col for col in cols]),
        values=', '.join(['%s' for col in values])
    )

    cursor.execute(insert_sql, values)
    conn.commit()


def tableToJson(table, result):
    config = json.load(open(CONFIG_FILE))
    conn = pymysql.connect(host=config['host'], user=config['user'], passwd=config['password'], db='question_pre',
                           port=3306, charset= "utf8", use_unicode=True, cursorclass = pymysql.cursors.DictCursor)
    cur = conn.cursor()

    sql = "select * from {0} WHERE question_id = '{1}' ".format(table, result)
    cur.execute(sql)
    data = cur.fetchall()

    if len(data) > 0:
        data = data[0]
        all_set = {'question_html', 'option_html', 'answer_all_html', 'jieda', 'fenxi', 'dianping'}
        for i in all_set:
            data[i] = get_pure_text_for_search(data[i])

        Data_to_MySQL(data)

    else:
        print(result)
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
    readTxt()