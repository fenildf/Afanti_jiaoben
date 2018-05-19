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
from PyPDF2 import PdfFileWriter,PdfFileReader
from reportlab.pdfgen import canvas
from collections import OrderedDict
from reportlab.lib.units import cm

LOGGING_FORMAT = '%(asctime)-15s:%(levelname)s: %(message)s'
logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO,
                    filename='working/pl_pdf_sy.log', filemode='a')

_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))).replace('\\', '/')
INPUT_PATH = _DIR + '/inputfile/PDF/'
MARK_PATH = _DIR + '/inputfile/MARK/'
OUT_PATH = _DIR + '/outputfile/PDF/'
CONFIG_FILE = os.path.join(_DIR, 'config')

def middle_watermark(content,filename):
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


def buttom_watermark(content,filename):
    '''
    :param content: 显现字符串
    :param filename: 水印文件名
    '''
    # 默认大小为21cm*29.7cm
    c = canvas.Canvas(MARK_PATH + filename, pagesize=(20 * cm, 20 * cm))
    # 移动坐标原点(坐标系左下为(0,0))
    c.translate(7 * cm, 1 * cm)

    # 设置字体Helvetica/Symbol/ZapfDingbats
    c.setFont("Symbol", 10)
    # 指定描边的颜色
    c.setStrokeGray(0.2)
    # 指定填充颜色
    # c.setFillGray(0.2)
    # 设置透明度，1为不透明
    c.setFillAlpha(0.3)
    # 画几个文本，注意坐标系旋转的影响
    c.drawString(1 * cm, 1 * cm, content)

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
    c.setFillAlpha(0.3)  # 设置透明度
    c.drawImage(MARK_PATH + f_jpg, 10 * cm, 1 * cm, 3 * cm, 1 * cm)  # 这里的单位是物理尺寸
    c.save()


def add_watermark(pdf_file_in, mark1, mark2):
    '''
    :param pdf_file_in: 传入文件
    :param mark1: 水印文件1
    :param mark2: 水印文件2
    '''
    pdf_output = PdfFileWriter()
    input_stream = open(INPUT_PATH + pdf_file_in, 'rb')
    pdf_input = PdfFileReader(input_stream)

    # PDF文件被加密了
    # if pdf_input.getIsEncrypted():
    #     print('该PDF文件被加密了.')
    #     # 尝试用空密码解密
    #     try:
    #         pdf_input.decrypt('')
    #     except Exception as e:
    #         print('尝试用空密码解密失败.')
    #         return False
    #     else:
    #         print('用空密码解密成功.')

    # 获取PDF文件的页数
    pageNum = pdf_input.getNumPages()
    # 读入水印pdf文件
    pdf_mark1 = PdfFileReader(open(MARK_PATH + mark1, 'rb'))
    pdf_mark2 = PdfFileReader(open(MARK_PATH + mark2, 'rb'))
    # 给每一页打水印
    for i in range(pageNum):
        page = pdf_input.getPage(i)
        page.mergePage(pdf_mark1.getPage(0))
        page.mergePage(pdf_mark2.getPage(0))
        page.compressContentStreams()  # 压缩内容
        pdf_output.addPage(page)

    outputStream = open(OUT_PATH + pdf_file_in, "wb")
    pdf_output.write(outputStream)


def getPDF():
    for root,dirs,files in os.walk(INPUT_PATH):
        if len(files) == 0:
            raise "{0}下没有文件！".format(INPUT_PATH)
    return files


if __name__ == '__main__':
    mark_pdf_web = 'mark2.pdf'
    mark_pdf_aft = 'mark.pdf'
    f_tupain = 'yunjiang.png'
    if os.path.exists(MARK_PATH + mark_pdf_web):
        os.remove(MARK_PATH + mark_pdf_web)
    if os.path.exists(MARK_PATH + mark_pdf_aft):
        os.remove(MARK_PATH + mark_pdf_aft)
    middle_watermark(content='fudao.afanti100.com', filename=mark_pdf_web)
    buttom_watermark(content='阿凡题1对1 内部资料',filename=mark_pdf_aft)
    # create_waterjpg(f_jpg=f_tupain, filename=mark_pdf_aft)
    filename_list = getPDF()
    for input_file in filename_list:
        add_watermark(
            pdf_file_in=input_file,
            mark1=mark_pdf_aft,
            mark2=mark_pdf_web
        )
    print("PDF has been finished!")
