# -*-coding:utf8-*-
import os
import sys
import json
import pymysql
import pymysql.cursors
import logging

LOGGING_FORMAT = '%(asctime)-15s:%(levelname)s: %(message)s'
logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO,
                                filename='working/question_count.log', filemode='a')

_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))).replace('\\', '/')
CONFIG_FILE = os.path.join(_DIR, 'config')
INPUT_PATH = _DIR + '/inputfile/'
input_file = 'questions.txt'

def Data_to_MySQL(datas):
    #采用同步的机制写入mysql
    config = json.load(open(CONFIG_FILE))
    conn = pymysql.connect(host=config['host'], user=config['user'], passwd=config['password'], db='question_pre',
                           port=3306, charset= "utf8", use_unicode=True, cursorclass = pymysql.cursors.DictCursor)
    cursor = conn.cursor()

    cols, values = zip(*datas.items())

    insert_sql = 'insert ignore into {table} ({cols}) values ({values})'.format(
        table='questions_txt_20171213',
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
    sql = "select * from {0} WHERE question_id = '{1}' ".format(table, result[0])
    cur.execute(sql)
    data = cur.fetchall()
    if len(data) > 0:
        data = data[0]
        data['knowledge_point'] = result[1]
        Data_to_MySQL(data)

    else:
        print(result[1])
        logging.info("the {0} is error".format(result[1]))


def readTxt():
    with open(INPUT_PATH + input_file, 'r', encoding='utf-8') as txt_file:
        while True:
            line = txt_file.readline()
            if line:
                result = line.replace('\n','').split('\t')
                tableToJson(
                    table='question',
                    result=result
                )

                pass
            else:
                break
        txt_file.close()



if __name__ == '__main__':
    readTxt()