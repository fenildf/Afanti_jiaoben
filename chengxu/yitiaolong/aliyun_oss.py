# -*-coding:utf8-*-
import os
import sys
import json
import platform
import oss2
try:
    import configparser as compat_configparser
except ImportError: # Python 2
    import ConfigParser as compat_configparser

_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))).replace('\\', '/')


class OssFeng(object):
    def __init__(self, config, OUTPUT_PATH, yuan):
        '''
        config: 包含各种信息, dict
        OUTPUT_PATH: 本地文件路径, str
        yuan: 源字段, str
        '''
        self._access_key_id = config['access_key_id']
        self._access_key_secret = config['access_key_secret']
        self._endpoint = config['endpoint']
        self._bucket_name = config['bucket_name']
        self.oss_path = config['oss_path']
        self.root = OUTPUT_PATH
        self.filename = self._getFile()
        self.yuan = yuan

        self.multipart_threshold = 10 * 1024 * 1024

        for param in config.values():
            assert '<' not in param, '请设置参数：' + param

        self.bucket = oss2.Bucket(oss2.Auth(
            self._access_key_id, self._access_key_secret), self._endpoint, self._bucket_name)

        if isinstance(yuan, int):
            self.yuan = str(yuan)


    def _getFile(self):
        for root, dirs, files in os.walk(self.root):
            if len(files) == 0:
                print("该路径{}下没有文件".format(self.root))
            return list(set(files))


    def upload(self):
        for fn in self.filename:
            fn_path = self.oss_path.format(self.yuan) + fn
            fn_root = self.root + fn
            total_size = os.path.getsize(fn_root)

            if total_size < self.multipart_threshold:
                self.bucket.put_object_from_file(fn_path, fn_root)

            else:
                part_size = oss2.determine_part_size(total_size, preferred_size=1024 * 1024)
                # 初始化分片上传，得到Upload ID。接下来的接口都要用到这个Upload ID。
                upload_id = self.bucket.init_multipart_upload(fn_path).upload_id
                # 逐个上传分片
                # 其中oss2.SizedFileAdapter()把fileobj转换为一个新的文件对象，
                # 新的文件对象可读的长度等于num_to_upload
                with open(fn_root, 'rb') as fileobj:
                    parts = []
                    part_number = 1
                    offset = 0
                    while offset < total_size:
                        num_to_upload = min(part_size, total_size - offset)
                        result = self.bucket.upload_part(fn_path, upload_id, part_number,
                                                    oss2.SizedFileAdapter(fileobj, num_to_upload))
                        parts.append(oss2.models.PartInfo(part_number, result.etag))

                        offset += num_to_upload
                        part_number += 1

                    # 完成分片上传
                    self.bucket.complete_multipart_upload(fn_path, upload_id, parts)

                # 验证一下
                with open(fn_root, 'rb') as fileobj:
                    assert self.bucket.get_object(fn_path).read() == fileobj.read(), \
                        "文件分片上传出错!{}".format(fn_path)


    def remove(self):
        file_path = []
        for fn in self.filename:
            file_path.append(self.oss_path.format(self.yuan) + fn)

        self.bucket.batch_delete_objects(file_path)

        # 确认Object已经被删除了
        for fn in file_path:
            assert not self.bucket.object_exists(fn)

    def download(self):
        path = self.oss_path.format(self.yuan)
        for filepath in oss2.ObjectIterator(self.bucket, prefix=path):
            # self.bucket.get_object_to_file(filepath.key, self.root + filepath.key.replace(path, ''))
            filename = self.root + filepath.key.replace(path, '')

            # 断点续传下载
            oss2.resumable_download(self.bucket, filepath.key, filename,
                                    multiget_threshold=1024 * 1024,
                                    part_size=256 * 1024,
                                    num_threads=3)

            # 验证一下
            result = self.bucket.get_object(filepath.key)
            content = b''
            for chunk in result:
                content += chunk

            with open(filename, 'rb') as fileobj:
                assert fileobj.read() == content, "该路径下文件{}内容出错！".format(filename)


    @property
    def config_file(self):
        return config

    @property
    def bucket_name(self):
        return self._bucket_name

    @property
    def endpoint(self):
        return self._endpoint

    @property
    def access_key_id(self):
        return self._access_key_id

    @access_key_id.setter
    def access_key_id(self, value):
        self._access_key_id = value

    @property
    def access_key_secret(self):
        return self._access_key_secret

    @access_key_secret.setter
    def access_key_secret(self, value):
        self._access_key_secret = value


def getConfig(config_file=None):
    # default config_file is ~/.osscredentials
    oss_name = 'OSSCredentials'
    if not config_file:
        config_file = os.path.join(
                os.path.expanduser('~'),
                '.osscredentials'
            )

    configparser = compat_configparser.ConfigParser()
    with open(config_file) as f:
        configparser.readfp(f)

    access_key_id = configparser.get(oss_name, 'accessid')
    access_key_secret = configparser.get(oss_name, 'accesskey')
    endpoint = configparser.get(oss_name, 'host')

    if not (access_key_id and access_key_secret and endpoint):
        return None
    config = {
        'access_key_id': access_key_id,
        'access_key_secret': access_key_secret,
        'endpoint': 'http://' + endpoint
    }
    return config


if __name__ == '__main__':
    file_path = '/outputfile/image_path/'
    yuan = '200'
    OUTPUT_PATH = _DIR + file_path
    BUCKET_NAME = 'afanti-question-images'
    oss_path = 'data/image/question_image/{}/'

    if 'Windows' in platform.system():
        CONFIG_FILE = os.path.join(_DIR, 'oss_config')
        config = json.load(open(CONFIG_FILE))
        config['bucket_name'] = BUCKET_NAME
        config['oss_path'] = oss_path
        OssFeng(
            config=config,
            OUTPUT_PATH=OUTPUT_PATH,
            yuan=yuan
        ).upload()


    elif 'Linux' in platform.system():
        config = getConfig()
        if isinstance(config, dict):
            config['bucket_name'] = BUCKET_NAME
            config['oss_path'] = oss_path
            OssFeng(
                config=config,
                OUTPUT_PATH=OUTPUT_PATH,
                yuan=yuan
            ).upload()
        else:
            raise FileNotFoundError("没有找到.osscredentials配置文件！")
