# -*-coding:utf8-*-
import os
import sys
import json
import re
import urllib
import requests
import logging
import hashlib
import pymysql
import time
import random
# from PDF import PdfFileReader,PdfFileWriter
from PyPDF2 import PdfFileWriter,PdfFileReader
from reportlab.pdfgen import canvas
from collections import OrderedDict
from reportlab.lib.units import cm

LOGGING_FORMAT = '%(asctime)-15s:%(levelname)s: %(message)s'
logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO,
                    filename='working/pdf_shuiyin.log', filemode='a')

_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))).replace('\\', '/')
INPUT_PATH = _DIR + '/inputfile/PDF/'
MARK_PATH = _DIR + '/inputfile/MARK/'
OUT_PATH = _DIR + '/outputfile/PDF/'
CONFIG_FILE = os.path.join(_DIR, 'config')
input_file = '2017.pdf'

subjects = {
    '1': '初中语文',
    '2': '初中数学',
    '3': '初中英语',
    '5': '初中物理',
    '6': '初中化学',
    '7': '初中地理',
    '8': '初中历史',
    '9': '初中生物',
    '10': '初中政治',
    '21': '高中语文',
    '22': '高中数学',
    '23': '高中英语',
    '25': '高中物理',
    '26': '高中化学',
    '27': '高中地理',
    '28': '高中历史',
    '29': '高中生物',
    '30': '高中政治',
    '42': '小学数学',

}

def create_watermark(content,filename):
    '''
    :param content: 显现字符串
    :param filename: 水印文件名
    '''
    # 默认大小为21cm*29.7cm
    c = canvas.Canvas(MARK_PATH + filename, pagesize=(30 * cm, 30 * cm))
    # 移动坐标原点(坐标系左下为(0,0))
    c.translate(8 * cm, 1 * cm)

    # 设置字体
    c.setFont("Helvetica", 20)
    # 指定描边的颜色
    c.setStrokeColorRGB(0, 0.5, 0)
    # 指定填充颜色
    c.setFillColorRGB(0, 0.5, 0)
    # 画一个矩形
    # c.rect(cm, cm, 7 * cm, 17 * cm, fill=1)

    # 旋转45度，坐标系被旋转
    c.rotate(45)
    # 指定填充颜色
    # c.setFillColorRGB(0, 0, 0)
    # 设置透明度，1为不透明
    c.setFillAlpha(0.1)
    # 画几个文本，注意坐标系旋转的影响
    c.drawString(2 * cm, 2 * cm, content)
    c.setFillAlpha(0.1)
    c.drawString(16 * cm, 16 * cm, content)

    # 关闭并保存pdf文件
    c.save()


def create_waterjpg(f_jpg, filename):
    '''
    :param f_jpg: 图片名
    :param filename: 水印文件名
    '''
    w_pdf = 20 * cm
    h_pdf = 20 * cm

    c = canvas.Canvas(MARK_PATH + filename, pagesize=(w_pdf, h_pdf))
    # c.setFillColorRGB(0, 0.5, 0)
    c.setFillAlpha(0.4)  # 设置透明度
    c.drawImage(MARK_PATH + f_jpg, 9 * cm, 1 * cm, 3 * cm, 0.6 * cm)  # 这里的单位是物理尺寸
    c.save()


def add_watermark(pdf_file_in, mark_list, pdf_file_out):
    pdf_output = PdfFileWriter()
    input_stream = open(pdf_file_in, 'rb')
    pdf_input = PdfFileReader(input_stream)

    # 获取PDF文件的页数
    pageNum = pdf_input.getNumPages()

    # 给每一页打水印
    for i in range(pageNum):
        page = pdf_input.getPage(i)
        for mark in mark_list:
            # 读入水印pdf文件
            page.mergePage(PdfFileReader(open(MARK_PATH + mark, 'rb')).getPage(0))
        page.compressContentStreams()  # 压缩内容
        pdf_output.addPage(page)

    outputStream = open(pdf_file_out, "wb")
    pdf_output.write(outputStream)
    logging.info(pdf_file_out)


def gendir():
    try:
        for sb in subjects.items():
            subject,sbname=sb
            os.makedirs(OUT_PATH + 'pdf_0307/{}'.format(sbname))
    except Exception as e:
        pass

if __name__ == '__main__':
    # gendir()
    mark_pdf_list = ['mark.pdf','mark2.pdf']
    # mark_pdf_web = 'mark2.pdf'
    # mark_pdf_aft = 'mark.pdf'
    f_tupain = 'afanti.png'
    for mark in mark_pdf_list:
        if os.path.exists(MARK_PATH + mark):
            os.remove(MARK_PATH + mark)
    create_watermark(content='fudao.afanti100.com',filename=mark_pdf_list[1])
    create_waterjpg(f_jpg=f_tupain,filename=mark_pdf_list[0])
    for root,dirs,files in os.walk(INPUT_PATH + 'pdf_0307'):
        for f in files:
            input_file = os.path.join(root, f)
            add_watermark(
                pdf_file_in=input_file,
                mark_list=mark_pdf_list,
                pdf_file_out=input_file.replace(INPUT_PATH,OUT_PATH)
            )
    print("PDF has been finished!")

