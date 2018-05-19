# -*- coding: utf-8 -*-

import os
import time
import email
from email.header import Header
from email.message import EmailMessage
import smtplib, datetime

from afanti_tiku_lib.dbs.mysql_pool import CommonMysql
from afanti_tiku_lib.dbs.execute import execute

# mysql = CommonMysql('format')
# mysql_conn = mysql.connection()


class MailSender:
    """封装发邮件"""

    def __init__(self):
        self.mymail = 'yanfeng.li@lejent.com'
        self.server = smtplib.SMTP()
        self.server.connect('smtp.exmail.qq.com')
        self.server.login(self.mymail, 'Lyf2319619')


    def close(self):
        self.server.close()

    def send(self, to_addrs, subject, content):
        """发邮件"""

        msg = EmailMessage()

        #主题
        # msg['Subject'] = Header(subject, 'utf-8')
        msg['Subject'] = subject
        msg['From'] = self.mymail
        msg['To'] = ','.join(to_addrs)
        msg.set_content(content)

        #正文
        self.server.sendmail(self.mymail, to_addrs, msg.as_string())


def get_msg(tms):
    sql = 'select count(*) from image_child'
    rows = execute(mysql_conn, sql)
    tcount = rows[0][0]

    tm_begin = time.localtime(tms - 1 * 60 * 60)
    tm_end = time.localtime(tms)

    begin = '{y}-{m}-{d} {h:0>2}:00:00'.format(y=tm_begin.tm_year, m=tm_begin.tm_mon, d=tm_begin.tm_mday, h=tm_begin.tm_hour)
    end = '{y}-{m}-{d} {h:0>2}:00:00'.format(y=tm_end.tm_year, m=tm_end.tm_mon, d=tm_end.tm_mday, h=tm_end.tm_hour)
    sql = 'select count(*) from image_child where "{}" <= add_time and "{}" > add_time'.format(
        begin, end
    )
    rows = execute(mysql_conn, sql)
    icount = rows[0][0]

    msg = ('总图片: {}\n'
           '{} ~ {}: {}\n'
           ).format(
               tcount,
               begin,
               end,
               icount,
           )
    return msg


def main():
    done = False
    while True:
        tms = time.time()
        tm = time.localtime(tms)
        if tm.tm_min != 0:
            time.sleep(10)
            if done:
                done = False
            continue
        else:
            if done:
                continue

        # content = get_msg(tms)
        content = 'this is laji'
        mailsender = MailSender()
        mailsender.send([
            '454552269@qq.com'
        ], '收集图片', content)
        mailsender.close()
        done = True


if __name__ == '__main__':
    # main()
    content = 'this is laji'
    mailsender = MailSender()
    mailsender.send  ([
        '454552269@qq.com'
    ], '收集图片', content)
    mailsender.close()