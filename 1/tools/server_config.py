"""
在服务器端的接受相机的配置



is_main 是否为主服务器
local_img_ip 对应的工控机的ip
local_img_port 对应工控机绑定的端口号 绑定的端口从9000开始
save_root 接受到图像后保存的地址
server_url 向spring boot 发送的url



"""

import os
from tools.env_variable import env
from tools.envs import ENV

cwd = os.getcwd()

config = dict()

config["is_main"] = True


if config["is_main"]:
    base_port = 9000
    config["local_img_ip"] = "192.168.137.50"
else:
    config["local_img_ip"] = "192.168.137.51"
    base_port = 9000 + 4
config["local_img_port"] = [base_port+i for i in range(4)]

if env == ENV.DEV:
    config["save_root"] = r"F:\tmp\data\i"
    config["local_img_ip"] = "127.0.0.1"
    config["server_url"] = "http://127.0.0.1:8082"


if env == ENV.PROD:
    config["save_root"] = r"D:\data\tmp"
    config["server_url"] = "http://192.168.137.101:8082"



if env == ENV.TEST:
    config["save_root"] = r"D:\data\tmp"
    config["server_url"] = "http://192.168.137.101:8082"

if env == ENV.TEST1:
    config["save_root"] = r"D:\data"
    config["server_url"] = "http://192.168.137.101:8082"
    config["local_img_ip"] = "192.168.137.101"

if env == ENV.CLOUD1:
    config["local_img_ip"] = "127.0.0.1"
    config["local_img_port"] = [base_port + i for i in range(4)]
    config["save_root"] ="/home/project/bangcai3/data/i"
    config["server_url"] = "http://127.0.0.1:8082"
    config["upload"] = True