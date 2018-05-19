# -*-coding:utf8-*-
import os
import sys
import logging

LOGGING_FORMAT = '%(asctime)-15s:%(levelname)s: %(message)s'
logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO,
                                filename='working/findurl.log', filemode='a')
_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))).replace('\\', '/')

WRT_SAM_PATH = _DIR + '/writing_sample/'
LOG_PATH = _DIR + '/writing_sample_log/'
OUT_PATH = _DIR + '/writing/'

sample_file = 'writing_sample_{}'
log_file = 'writing_sample_{}.log'
output_file = 'writing_{}.txt'
subj_set = {'1','2','8','10','21','28','30','41','42','48','50'}
# subj_set = {'2'}

def findUrl():
    for subj in subj_set:
        txtfile = OUT_PATH + output_file.format(subj)
        if os.path.exists(txtfile):
            os.remove(txtfile)

        logging.info("find url in {0}".format(subj))
        short = set([])
        with open(LOG_PATH + log_file.format(subj), 'r') as smallfile:
            shorts = smallfile.readlines()
            smallfile.close()
        for s in shorts:
            short.add(s.replace('\n', '').split(' ')[0])
        del shorts

        with open(WRT_SAM_PATH + sample_file.format(subj), 'r') as bigfile:
            result = bigfile.readlines()
            bigfile.close()

        max_len = len(short)
        flag_len = 0
        exit_flag = False
        for ss in short:
            for r in result:
                if ss in r:
                    flag_len += 1
                    exit_flag = True
                    with open(OUT_PATH + output_file.format(subj), 'a') as newfile:
                        newfile.write(r)
                        newfile.close()
                    break
            if flag_len >= max_len:
                break


if __name__ == '__main__':
    findUrl()
