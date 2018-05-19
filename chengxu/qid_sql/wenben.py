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
                                filename='working/wenben.log', filemode='a')

_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))).replace('\\', '/')
INPUT_PATH = _DIR + '/inputfile/'
OUT_PATH = _DIR + '/outputfile/'
CONFIG_FILE = os.path.join(_DIR, 'config')
input_file = '111.qid'
output_file = '222.txt'


def tableToJson(table, result):
    config = json.load(open(CONFIG_FILE))
    conn = pymysql.connect(host=config['host'], user=config['user'], passwd=config['password'], db='question_pre',
                           port=3306, charset= "utf8", use_unicode=True, cursorclass = pymysql.cursors.DictCursor)
    cur = conn.cursor()

    sql = "select latex_question from {0} WHERE question_id = '{1}' ".format(table, result)
    cur.execute(sql)
    data = cur.fetchall()

    if len(data) > 0:
        data = data[0]
        latex_question = data['latex_question']

        with open(OUT_PATH + output_file, 'a', encoding='utf-8') as ot_file:
            ot_file.write(result + '\t' + latex_question + '\n')

    else:
        logging.error("解读到{0}时，没有相应question_id".format(result))


def readTxt():
    with open(INPUT_PATH + input_file, 'r', encoding='utf-8') as txt_file:
        while True:
            line = txt_file.readline()
            if line:
                result = line.replace('\n','')
                tableToJson(
                    table='question_search',
                    result=result
                )

            else:
                break
        txt_file.close()



if __name__ == '__main__':
    if os.path.exists(output_file):
        os.remove(output_file)
    readTxt()