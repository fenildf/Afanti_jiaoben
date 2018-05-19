# -*-coding:utf8-*-
import os
import sys
import logging
import csv
import json
import pymysql
import pymysql.cursors
from PowerRing import render_question_dict


LOGGING_FORMAT = '%(asctime)-15s:%(levelname)s: %(message)s'
logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO,
                                filename='working/UCweb.log', filemode='a')
_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))).replace('\\', '/')
INPUT_PATH = _DIR + '/inputfile/'
OUT_PATH = _DIR + '/outputfile/'
CONFIG_FILE = os.path.join(_DIR, 'config')
input_file = 'diff_result.csv'
output_file = ''


def Data_to_MySQL(datas):
    #采用同步的机制写入mysql
    config = json.load(open(CONFIG_FILE))
    conn = pymysql.connect(host=config['host'], user=config['user'], passwd=config['password'], db='question_pre',
                           port=3306, charset= "utf8", use_unicode=True, cursorclass = pymysql.cursors.DictCursor)
    cursor = conn.cursor()

    cols, values = zip(*datas.items())

    insert_sql = 'insert ignore into {table} ({cols}) values ({values})'.format(
        table='knowledge_sample',
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
        qid_html = render_question_dict(data)
        return qid_html

    else:
        logging.error("解读到{0}时，没有相应question_id".format(result))
        print(result)


def readCsvData():
    with open(INPUT_PATH + input_file, 'r', encoding='gbk') as raw_file:
        jobs = csv.DictReader(raw_file)
        for job in jobs:
            qid_html = tableToJson(
                table='question',
                result=job['qid']
            )
            job['qid_html'] = qid_html

            data_dict = {
                'subject_match': '',
                'qid_match': '',
                'knowledge_new_correct': '',
                'knowledge_old_correct': '',
                'evaluate_complete': 0,
                'knowledge_match': '',
                'knowledge_fix': '',
                'ocr_result':''
            }
            result = dict(data_dict, **job)
            Data_to_MySQL(result)

        raw_file.close()


if __name__ == '__main__':
    readCsvData()