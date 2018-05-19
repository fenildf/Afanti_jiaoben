# -*-coding:utf8-*-
import os
import sys
import json
import logging
from collections import OrderedDict
import pymysql
import pymysql.cursors

LOGGING_FORMAT = '%(asctime)-15s:%(levelname)s: %(message)s'
logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO,
                                filename='working/shenma.log', filemode='a')

_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))).replace('\\', '/')
OUT_PATH = _DIR + '/outputfile/'
output_file = 'first_json.txt'

config = {
    "host":"10.170.251.183",
    "user":'root',
    "password":'123',
    "db":"hanyu_gaolaoshi",
    "port":13309
}

lizi = {
    "first_classification":"季节的成语",
    "second_classification":"描写春天的成语",
    "idiom":"秋实春华",
    "meaning":"比喻德行和才华。",
    "second_classification_url":"http://hanyu.afanti100.com/hanyu/idiom/group/550"
}
URL = "http://hanyu.afanti100.com/hanyu/idiom/group/"


def secondTable(first_name, group_id):
    #采用同步的机制写入mysql
    conn = pymysql.connect(host=config['host'], user=config['user'], passwd=config['password'],
                           db=config['db'], port=config['port'], charset="utf8",
                           use_unicode=True, cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()

    sql1 = "select words_name,words_basic_explanation,group_name from {0} WHERE group_id = '{1}' ".format('sub_group', group_id)
    cursor.execute(sql1)
    data = cursor.fetchall()
    new_list = []
    for sd in data:
        dd = OrderedDict()
        dd["first_classification"] = first_name
        dd["second_classification"] = sd['group_name']
        dd["idiom"] = sd['words_name']
        dd["meaning"] = sd['words_basic_explanation']
        dd["second_classification_url"] = URL + str(group_id)
        new_list.append(dd)

    return new_list


def tableToJson(table, group_type):
    all_list = []
    conn = pymysql.connect(host=config['host'], user=config['user'], passwd=config['password'],
                           db=config['db'],port=config['port'], charset= "utf8",
                           use_unicode=True, cursorclass = pymysql.cursors.DictCursor)
    cur = conn.cursor()
    sql = "select group_id,group_view_name from {0} WHERE group_type = '{1}' ".format(table, group_type)

    cur.execute(sql)
    data = cur.fetchall()

    if len(data) > 0:
        for dd in data:
            group_id = dd['group_id']
            first_name = dd['group_view_name']
            new_list = secondTable(
                group_id=group_id,
                first_name=first_name
            )
            all_list.extend(new_list)

        with open(OUT_PATH + output_file, 'wt', encoding='utf-8') as ot_file:
            ot_file.write(json.dumps(all_list))
            ot_file.close()

def ceshi():
    with open(OUT_PATH + output_file, 'r', encoding='utf-8') as old_file:
        a = old_file.readlines()
        b = json.loads(a[0])
        print(len(b))
        old_file.close()

if __name__ == '__main__':
    # tableToJson(
    #     table='first_group',
    #     group_type=3
    # )
    ceshi()
