# -*-coding:utf8-*-
import os
import sys
import requests
import urllib
import re
import logging
import time
import json
import imghdr

LOGGING_FORMAT = '%(asctime)-15s:%(levelname)s: %(message)s'
logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO,
                    filename='working/xingjinzi.log', filemode='a')
_DIR = os.path.dirname(os.path.abspath(__file__)).replace("\\", '/')
XJZ_PATH = _DIR + '/xingjinzi/'
xjz_file = 'xjz_file.txt'

URL = 'http://www.fantizi5.com/xingjinzi/json/{0}.html?timestamp={1}'

Headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Host': 'www.fantizi5.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Referer': 'http://www.fantizi5.com/xingjinzi/',
    'X-Request-With': 'XMLHttpRequest',
    'Connection': 'keep-alive'
}

def zhhanzi(hex_str):
    return chr(eval('0x' + hex_str))


if __name__ == '__main__':
    with open('yanfeng.hanyu', 'r', encoding='utf-8') as f:
        s = f.readlines()
    # s = ['郎\n', '天\n', '发\n']
    for i in range(1,len(s)):
        time.sleep(0.2)
        hanzi = s[i].replace('\n', '').encode('utf8')
        # print(hanzi)
        hanzi_str = ''.join(re.findall('\\\\x(..)', str(hanzi)))

        postdata = requests.post(URL.format(hanzi_str, int(time.time())), headers=Headers, timeout=100)
        if postdata.status_code == 200:
            if len(postdata.text) > 0:
                pdata_list = postdata.text.split('$')
                data_str = ';'.join([zhhanzi(pd) for pd in pdata_list])

                with open(XJZ_PATH + xjz_file, 'a', encoding='utf-8') as new_file:
                    new_file.write(s[i].replace('\n', '\t'))
                    new_file.write(data_str)
                    new_file.write('\n')
            else:
                logging.info("文字 :{0}在hanyu的第{1}行，请求成功，但没有对应形近字,".format(hanzi, i))

        else:
            logging.error("文字 :{0} 没有形近字,在hanyu的第{1}行".format(hanzi, i))

