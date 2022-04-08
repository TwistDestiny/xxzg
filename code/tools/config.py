# """
# flask_server_port flask 绑定的端口
# is_main 是否为主工控机
# local_img_ip 为相机缓存服务绑定的ip
# local_img_port 为相机缓存服务绑定的端口
# pfs_list 为配置文件存储的位置
# sample_img_path 为模拟测试的图的保存目录
# server_url 为AI向主服务器发送数据的url
# """
#
# import os
# from tools.env_variable import env
# from tools.envs import ENV
#
# cwd = os.getcwd()
#
# config = dict()
# config["flask_server_port"] = 8007
# config["thread_num"] = 16
# # config["save_root"] = r"F:\data\tmp"
# config["is_main"] = False
# if env == ENV.PROD1:
#     config["is_main"] = True
#
# if config["is_main"]:
#     base_port = 9000
# else:
#     base_port = 9000
#
# config["border_ratio"] = 0
# config["use_light"] = True
#
#
# if env == ENV.DEV:
#     config["server_url"] = "http://localhost:8082"
#     # config["img_server_url"] = "http://localhost:8008"
#     config["local_img_ip"] = "127.0.0.code"
#     config["local_img_port"] = [base_port+i for i in range(4)]
#     config["sample_img_path"] = r'D:\test.jpg'
#
#
# if env == ENV.PROD1:
#     config["server_url"] = "http://192.168.91.101:8082"
#     # config["img_server_url"] = "http://localhost:8008"
#     config["pfs_list"] = [r"D:\code\config_file\camera_config\config2\{}.pfs".format(i) for i in range(4)]
#     config["local_img_ip"] = "192.168.90.50"
#     config["local_img_port"] = [base_port + i for i in range(4)]
#     config["sample_img_path"] = r'D:\test.jpg'
#     config["camera_ip_list"] = ["192.168.180.2", "192.168.186.2", "192.168.182.2", "192.168.183.2"]
#     config["edge_save"] = r"D:\data\edge"
#     config["camera_begin_id"] = 0
#
# if env == ENV.PROD2:
#     config["server_url"] = "http://192.168.91.102:8082"
#     # config["img_server_url"] = "http://localhost:8008"
#     config["pfs_list"] = [r"E:\code\config_file\camera_config\config2\{}.pfs".format(i) for i in range(4)]
#     config["local_img_ip"] = "192.168.90.51"
#     config["local_img_port"] = [base_port + i for i in range(4)]
#     config["sample_img_path"] = r'D:\test.jpg'
#     config["camera_ip_list"] = ["192.168.184.2", "192.168.187.2", "192.168.181.2", "192.168.185.2"]
#     config["edge_save"] = r"E:\data\edge"
#     config["camera_begin_id"] = 4
# if env == ENV.PROD2_TMP:
#     config["server_url"] = "http://192.168.91.101:8082"
#     # config["img_server_url"] = "http://localhost:8008"
#     config["pfs_list"] = [r"E:\code\config_file\camera_config\config2\{}.pfs".format(i) for i in range(4)]
#     config["local_img_ip"] = "192.168.90.51"
#     config["local_img_port"] = [base_port + i for i in range(4)]
#     config["sample_img_path"] = r'D:\test.jpg'
#     config["camera_ip_list"] = ["192.168.184.2", "192.168.187.2", "192.168.181.2", "192.168.185.2"]
#     config["edge_save"] = r"E:\data\edge"
#     config["camera_begin_id"] = 4
#
#     config["border_ratio"] = 0
#     config["use_light"] = True
#     config["is_main"] = True
#
# if env == ENV.TEST:
#     config["server_url"] = "http://192.168.137.101:8082"
#     # config["img_server_url"] = "http://localhost:8008"
#     config["pfs_list"]= [r"E:\download\feature\soft-trigger\raL2048-48gm_23709094.pfs" for i in range(4)]
#     config["pfs_list"] = [r"E:\download\feature\soft-trigger\trigger.pfs" for i in range(4)]
#     config["local_img_ip"] = "192.168.137.50"
#     config["local_img_port"] = [base_port + i for i in range(4)]
#     config["sample_img_path"] = r'D:\test.jpg'
# if env == ENV.TEST1:
#     config["server_url"] = "http://192.168.137.101:8082"
#     # config["img_server_url"] = "http://localhost:8008"
#     config["pfs_list"]= [r"E:\download\feature\soft-trigger\raL2048-48gm_23709094.pfs" for i in range(4)]
#
#     config["pfs_list"] = [r"E:\download\feature\soft-trigger\trigger.pfs" for i in range(4)]
#     config["local_img_ip"] = "192.168.137.101"
#     config["local_img_port"] = [base_port + i for i in range(4)]
#     # config["save_root"] = r"D:\data\tmp"
#     config["sample_img_path"] = r'D:\test.jpg'
#
# if env == ENV.CLOUD1:
#     config["server_url"] = "http://127.0.0.1:8082"
#     config["local_img_ip"] = "127.0.0.code"
#     config["local_img_port"] = [base_port + i for i in range(4)]
#     config["sample_img_path"] = "/home/data/test.jpg"

import os
from tools.utils import parseYaml
import os
import sys
join = os.path.join

root = os.path.dirname(os.path.dirname(__file__))
if os.path.exists(join(root,"resource")):
    env = parseYaml(join(root,"resource","static","config","env.yaml"))['mode']
    name = parseYaml(join(root,"resource","static","config","env.yaml"))['name']
    config = parseYaml(join(root,"resource","static","config","{}.yaml".format(env)))
else:
    env_dist = os.environ
    if "wx_resource" in env_dist:
        env = parseYaml(join(env_dist["wx_resource"], "static", "config", "env.yaml"))['mode']
        name = parseYaml(join(env_dist["wx_resource"],  "static", "config", "env.yaml"))['name']
        config = parseYaml(join(env_dist["wx_resource"], "static", "config", "{}.yaml".format(env)))
    else:
        raise Exception("找不到resource资源文件")

config["name"] = name
config["mode"] = env
if name in config:
    for key in config[name]:
        config[key] = config[name][key]