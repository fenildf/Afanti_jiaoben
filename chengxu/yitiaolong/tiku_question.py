# -*-coding:utf8-*-
import os
import sys
import json
import re
import pymysql
import pymysql.cursors
import logging
import hashlib
from simple_orm import sync_db as db
from simple_orm.simple_db_key_store import get_db_info
from tiku_lib.text import get_pure_text_for_search
from tiku_lib.html.img_url import extract_image_infos, base64_decode_img
from multiprocessing import Pool

'''
题目几个一组存在一个json文件里，格式如下，大约有1800个json文件，放在/data_ext/shared_data/kuaiyidian/json下面了。

[
    {
        "spider_source": 101, # 快易典
        "subject": 43,
        "question_body": "<img src=\"base64...\"",
        "option": "",
        "answer": "",
        "analy": "",
        "solution": "",
        "comment": ""
    }
]
其中HTML类字段(question_body、option、answer、analy、solution、comment)中图片是用base64直接编码在HTML代码中，需要导出为图片文件，上传到服务器，并修改对应图片链接。 
需要注意的是图片现在分为两类，一种是基本的img标签，另外一种是svg中的image标签。
http://git.lejent.cn/Spider/tiku_lib/blob/master/tiku_lib/html/img_url.py extract_image_infos
'''

LOGGING_FORMAT = '%(asctime)-15s:%(levelname)s: %(message)s'
logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO,
                                filename='working/tiku_question.log', filemode='a')

_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))).replace('\\', '/')
CONFIG_FILE = os.path.join(_DIR, 'config')
INPUT_PATH = _DIR + '/inputfile/'
OUTPUT_PATH = _DIR + '/outputfile/image_path/'
input_file = 'new.json'


def get_md5(url):
    if isinstance(url, str):
        md5 = hashlib.new('md5', url.encode('utf8')).hexdigest()
    elif isinstance(url, bytes):
        md5 = hashlib.new('md5', url).hexdigest()
    return md5


def dataToSql(datas):
    config = json.load(open(CONFIG_FILE))
    conn = pymysql.connect(host=config['host'], user=config['user'], passwd=config['password'], db='question_db_offline',
                           port=3306, charset="utf8", use_unicode=True, cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()

    cols, values = zip(*datas.items())

    insert_sql = 'insert ignore into {table} ({cols}) values ({values})'.format(
        table='kuaiyidian_20171227',
        cols=', '.join(['`%s`' % col for col in cols]),
        values=', '.join(['%s' for col in values])
    )

    cursor.execute(insert_sql, values)
    conn.commit()


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
    data_dict['exam_year'] = ''
    data_dict['exam_city'] = ''
    data_dict['question_quality'] = ''
    data_dict['jieda'] = data_dict['solution']
    del data_dict['solution']
    data_dict['question_type'] = int(data_dict['question_type'])

    return data_dict


def getSvgImage(data_str, filename):
    if len(data_str) > 0:
        if '<svg' in data_str and '<image href=' in data_str:
            svg_list = re.findall('<image href="(.+?)"', data_str)
            for svg in svg_list:
                _, img_content, ext = base64_decode_img(svg)
                svgname = get_md5(img_content) + ext
                data_str = data_str.replace(svg,
                    'http://qimg.afanti100.com/data/image/question_image/101/' + svgname).replace(
                    '<image href','<image xlink:href')
                # with open(OUTPUT_PATH + svgname, 'wb') as svgfile:
                #     svgfile.write(img_content)
                #     svgfile.close()

        else:
            res_lst = extract_image_infos(data_str)
            for res in res_lst:
                _,img_content, ext = base64_decode_img(res)
                resname = get_md5(img_content) + ext
                data_str = data_str.replace(res,
                    'http://qimg.afanti100.com/data/image/question_image/101/' + resname)
                # with open(OUTPUT_PATH + resname, 'wb') as resfile:
                #     resfile.write(img_content)
                #     resfile.close()
        return data_str


def dealImage(data_dict, filename):
    data_dict['question_body'] = getSvgImage(data_dict['question_body'], filename)
    data_dict['option'] = getSvgImage(data_dict['option'], filename)
    data_dict['answer'] = getSvgImage(data_dict['answer'], filename)
    data_dict['analy'] = getSvgImage(data_dict['analy'], filename)
    data_dict['solution'] = getSvgImage(data_dict['solution'], filename)
    data_dict['comment'] = getSvgImage(data_dict['comment'], filename)
    return data_dict


def readJson(root, filename):
    with open(root + filename, 'r', encoding='utf-8') as new_file:
        data_str = new_file.readline()
        try:
            data_json = json.loads(data_str)
            del data_str
            for data in data_json:
                data_dict = dealImage(data, filename)
                del data
                data_dict = dealDict(data_dict)
                dataToSql(data_dict)

        except Exception as e:
            print(filename)
            print(e)
            # raise NameError("readJson")
        new_file.close()


def file_name():
    for root, dirs, files in os.walk(INPUT_PATH + 'json/'):
        return root, files

if __name__ == '__main__':
    pool = Pool(3)
    root, files = file_name()
    for filename in files:
        # readJson(root=root, filename=filename)
        pool.apply_async(readJson, kwds={
            "root":root,
            "filename":filename
        })
    pool.close()
    pool.join()



