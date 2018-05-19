# -*-coding:utf8-*-
import os
import sys
import requests
import urllib
import re
import logging
import time
import json
import xlrd
import openpyxl

LOGGING_FORMAT = '%(asctime)-15s:%(levelname)s: %(message)s'
logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO,
                    filename='working/xingjinzi.log', filemode='a')
_DIR = os.path.dirname(os.path.abspath(__file__)).replace("\\", '/')
XJZ_PATH = _DIR + '/xingjinzi/'
inputfile = 'fangzi.xlsx'


def readMathXlsx():
    workbook = xlrd.open_workbook(inputfile)
    booksheet = workbook.sheet_by_name(u'sheet1')
    values = booksheet._cell_values
    URL= 'https://ihotel.meituan.com/group/v1/yf/list/{0}?{1}'
    Header = {
        "__skcy": "no-signature",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, sdch, br",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Connection": "keep-alive",
        "Content-Type": "application/json; charset=utf-8",
        "Cookie": "IJSESSIONID=k0eyv5zv1f4ibtfm0pz3y2w; iuuid=943447CDCECEAD76F20D3241E878189C61B766BB5311C327413CF3CCF1914A94; latlng=39.992981%2C116.328735%2C1516005858108; ci=1; cityname=%E5%8C%97%E4%BA%AC; _lxsdk_s=49e80e2fc83b1732eb9960f6e063%7C%7C35",
        "Host": "ihotel.meituan.com",
        "Origin": "http://i.meituan.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"
    }

    for i in range(1, len(values)):
        poild = int(values[i][0])
        data_dict = {
            "utm_medium": "touch",
            "version_name": "999.9",
            "platformid": "1",
            "start": "1515945600000",
            "end": "1516032000000",
            "type": "1",
            "poi": str(poild),
            "iuuid": "943447CDCECEAD76F20D3241E878189C61B766BB5311C327413CF3CCF1914A94",
            "_token": "eJxNT9tuglAQ/JfzKuFcALkkTQOiLbaIChUv8QHhFFBuCkKw6b/3mGjSzSYzszuZ7P6AixUBDSNWIgdaegEawDzih4ADTc02Eh4ijPFQlVSFA+H/mYwQIRw4XFYm0HYKkjgVy/v7YMn0DqsEcRgpaM89ucg4EVnfXRYzgaRpKg3ClM9p2lyDgg/LHAZdBRMJJmVDM1iVKYxokPFJk2evTFnRiyIIhB0IWEzusRiGpwcGD2ye2mYfMW+dxgVjdNplN692415f6LOR7E9GN3luXT7eXYOS5duoPFsxNsRB7+VrqjdSFJuBqbvZurec/DuK+/BUJ50Urs7H2aqYplYZO7TVqRd0vu8Qz7X1UrbGvZFvbSGN8dYW/Q45X5uCkqo9zMebBRaOWKFXNCXCQDgc5+OTaZ/hsv2QJGWwMCawTz7B7x9y0XfR"
        }
        data_str = urllib.parse.urlencode(data_dict)
        html = requests.get(URL.format(str(poild), data_str),headers=Header)
        if html.status_code == 200:
            html.encoding = 'utf-8'
            html_text = html.text
            if isinstance(html_text,str):
                html_json = json.loads(html_text)
                result_list = html_json['data']['result']
                for result in result_list:
                    tagName = result['tagName']

        name = values[i][1]
        values[i][2] = 2



if __name__ == '__main__':
    readMathXlsx()
    print('asd')