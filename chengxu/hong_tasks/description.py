# -*-coding:utf8-*-
import os
import sys
import xlrd
import json
import logging
import pymysql
import pymysql.cursors
import re

LOGGING_FORMAT = '%(asctime)-15s:%(levelname)s: %(message)s'
logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO,
                                filename='working/wenben.log', filemode='a')

_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))).replace('\\', '/')
INPUT_PATH = _DIR + '/inputfile/'
OUT_PATH = _DIR + '/outputfile/'
CONFIG_FILE = os.path.join(_DIR, 'config')
input_file = u'知识释义_数理化分开版.xlsx'
output_file = '222.txt'


def tableToJson(table, description, hkey):
    config = json.load(open(CONFIG_FILE))
    conn = pymysql.connect(host=config['host'], user=config['user'], passwd=config['password'],
                           db='tiku_cloud',port=3306, charset= "utf8", use_unicode=True,
                           cursorclass = pymysql.cursors.DictCursor)
    cur = conn.cursor()

    sql = "update {0} set description = '{1}' WHERE hkey = '{2}' ".format(table, description, hkey)
    try:
        cur.execute(sql)
    except:
        print(sql)


def readMathXlsx():
    workbook = xlrd.open_workbook(INPUT_PATH + input_file)
    booksheet = workbook.sheet_by_name(u'数学')
    # for i in range(1, booksheet.nrows):
    #     hkey = booksheet.cell(i, 0).value
    #     desc = booksheet.cell(i, 3).value
    #     print(cel)
    values = booksheet._cell_values
    for i in range(1, len(values)):
        hkey = values[i][0]
        desc = values[i][3]
        if isinstance(desc, str) and len(desc) > 0:
            desc = values[i][3].replace("'", '"')
            desc = re.findall('math(.+)', desc)[0]
        if len(desc) > 0:
            if desc[0] ==  '：':
                desc = desc[1:]
            tableToJson(
                hkey=hkey,
                table='knowledge',
                description=desc
            )


def readXlsx():
    workbook = xlrd.open_workbook(INPUT_PATH + input_file)
    for subj in {u"化学", u"物理"}:
        booksheet = workbook.sheet_by_name(subj)
        values = booksheet._cell_values
        for i in range(1, len(values)):
            hkey = values[i][0]
            desc = values[i][3]
            if isinstance(desc, str):
                desc = desc.replace("'", '"')
            if len(desc) > 0:
                tableToJson(
                    hkey=hkey,
                    table='knowledge',
                    description=desc
                )


if __name__ == '__main__':
    readMathXlsx()
    # readXlsx()
