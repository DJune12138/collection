import argparse
import json
import datetime
import services
from config import *
from utils.logger import Logger
from utils.mysql import MySQL, RepetitiveConnect as mysql_repetitive
from utils.redis import Redis, RepetitiveConnect as redis_repetitive


def __get_argv():
    """
    检验并加载公共脚本传参
    """

    # 1.获取脚本传参
    if services.argv is None:  # 防止加载一次后再次加载
        parser = argparse.ArgumentParser(description='欢迎使用Collection3！详细使用方法请查看README。')
        for parser_dict in p_parser.values():
            for parser_name, parser_setting in parser_dict.items():
                parser.add_argument('-' + parser_setting[pk_simple], '--' + parser_name, metavar=parser_name,
                                    help=parser_setting[pk_help])
        argv = parser.parse_args()
        argv.main_key_dict = dict()  # 引擎用，用于记录开启哪一块的业务

        # 2.校验脚本传参
        # 主参数，至少有一个
        main_list = p_parser[pk_main].keys()
        for parser_name in main_list:
            codes = getattr(argv, parser_name.replace('-', '_'))
            if codes is not None:
                argv.main_key_dict[parser_name] = codes
        if len(argv.main_key_dict) < 1:
            raise ValueError('主参数（%s）至少有一个！' % '、'.join(main_list))

        # 3.校验通过，加载公共脚本传参
        services.argv = argv


def __get_now_datetime():
    """
    记录项目启动时刻的datetime对象
    """

    if services.now_datetime is None:
        services.now_datetime = datetime.datetime.now()


def __get_redis():
    """
    加载Redis数据库连接池
    """

    if services.redis is None:
        services.redis = dict()
        with open('%s/redis.json' % account_name, 'r') as f:
            redis_account = json.load(f)
        for name, info in redis_account.items():
            try:
                services.redis[name] = Redis(**info)
            except redis_repetitive:
                services.logger.exception('Redis数据库（%s）重复连接！' % name)


def __get_logger():
    """
    根据配置，加载公共日志器
    """

    if services.logger is None:
        lc = dict()
        for k, v in logger_config.items():
            if v is not None:
                lc[k] = v
        services.logger = Logger(**lc).logger


def __get_mysql():
    """
    加载MySQL数据库连接池
    """

    if services.mysql is None:
        services.mysql = dict()
        with open('%s/mysql.json' % account_name, 'r') as f:
            mysql_account = json.load(f)
        for name, info in mysql_account.items():
            try:
                services.mysql[name] = MySQL(**info)
            except mysql_repetitive:
                services.logger.exception('MySQL数据库（%s）重复连接！' % name)


def load():
    """
    加载所有服务
    """

    __get_argv()
    __get_now_datetime()
    __get_redis()
    __get_logger()
    __get_mysql()
