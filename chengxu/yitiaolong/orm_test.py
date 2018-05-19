# -*-coding:utf8-*-
import os
import sys
import json
import hashlib
from simple_orm.simple_db_key_store import get_db_info
from simple_orm import sync_db as db
from tiku_lib.text import get_pure_text_for_search
'''
http://git.lejent.cn/Spider/async_db_orm
'''

_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))).replace('\\', '/')
INPUT_PATH = _DIR + '/inputfile/'

def get_md5(url):
    md5 = hashlib.new('md5', url.encode('utf8')).hexdigest()
    return md5


def dataToSql(question_dict, db):
    db.insert('kuaiyidian_20171227', **question_dict)


def dealDict(data_dict):
    data_dict['dianping'] = data_dict['comment']
    del data_dict['comment']
    spider_url = get_md5(get_pure_text_for_search(data_dict['paper_name_abbr']))
    data_dict['spider_url'] = 'kyd_' + spider_url + '/' + data_dict['question_id']
    del data_dict['question_id']
    data_dict['flag'] = 0
    data_dict['fenxi'] = data_dict['analy']
    del data_dict['analy']
    data_dict['answer_all_html'] = data_dict['answer']
    del data_dict['answer']
    data_dict['option_html'] = data_dict['option']
    del data_dict['option']
    data_dict['question_html'] = data_dict['question_body']
    del data_dict['question_body']
    data_dict['knowledge_point'] = ''
    data_dict['zhuanti'] = ''
    data_dict['exam_year'] = 2017
    data_dict['exam_city'] = ''
    data_dict['question_quality'] = 0
    data_dict['jieda'] = data_dict['solution']
    del data_dict['solution']
    data_dict['question_type'] = int(data_dict['question_type'])

    return data_dict


def readJson(root, fn, db):
    with open(root + fn, 'r', encoding='utf-8') as new_file:
        data_str = new_file.readline()
        try:
            data_json = json.loads(data_str)
            del data_str
            for data in data_json:
                question_dict = dealDict(data)
                dataToSql(question_dict, db)
                pass

        except Exception as e:
            print(fn)
            print(e)
            # raise NameError("readJson")
        new_file.close()


def file_name():
    for root, dirs, files in os.walk(INPUT_PATH + 'json/'):
        return root, files


if __name__ == '__main__':
    # pool = Pool(3)
    root, files = file_name()
    db_info = get_db_info('question_db_offline')
    db.create_conn(**db_info)
    for fn in files:
        readJson(root, fn, db)