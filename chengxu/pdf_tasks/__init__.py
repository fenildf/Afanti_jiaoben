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
from collections import OrderedDict

LOGGING_FORMAT = '%(asctime)-15s:%(levelname)s: %(message)s'
logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO,
                    filename='working/baidu_idiom_bulou.log', filemode='a')

_DIR = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')



