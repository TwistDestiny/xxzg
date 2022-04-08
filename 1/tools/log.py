#!/usr/bin/env python
#_*_coding:utf-8_*_
# vim : set expandtab ts=4 sw=4 sts=4 tw=100 :

import logging
import datetime
from logging.handlers import TimedRotatingFileHandler

import os

# 创建全局log句柄


#日志打印格式
log_fmt = '%(asctime)s\tFile \"%(filename)s\",line %(lineno)s\t%(levelname)s: %(message)s'
formatter = logging.Formatter(log_fmt)
#创建TimedRotatingFileHandler对象
os.makedirs('./logs', exist_ok=True)
now = datetime.datetime.now().strftime("./logs/%Y-%m-%d_%H-%M-%S.txt")
log_file_handler = TimedRotatingFileHandler(filename=now, when="S", interval=3600, backupCount=168) # 备份7 24*7天的
log_file_handler.suffix = "%Y-%m-%d_%H-%M-%S.log"
log_file_handler.setFormatter(formatter)
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()
log.addHandler(log_file_handler)



