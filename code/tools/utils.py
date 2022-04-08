import requests
import time
import datetime
import yaml
from tools.log import log
# from obs import ObsClient
import os
def ex():
    os.popen('taskkill /pid {} /f'.format(os.getpid()))
def postMsg(values_json,url):
    """

    :param values_json:收到的json序列化字符串
    :return:
    """
    # url = "http://{}:8080/ai/rects".format(config["serverIp"])
    try:
        headers = {"Content-Type": "application/json"}
        req = requests.post(url, data=values_json, headers=headers)
    except Exception as e:
        log.info("Post发送错误{}".format(repr(e)))
def get_id():
    trigger_time = datetime.datetime.now()
    time_stamp = time.mktime(trigger_time.timetuple()) + trigger_time.microsecond / 1E6
    trigger_id = int(time_stamp*1000)
    return trigger_id

def parseYaml(yaml_file=""):
    """
    :param yaml_file: yaml路劲
    :return: 数据字典
    """

    file = open(yaml_file, 'r', encoding="utf-8")
    file_data = file.read()
    file.close()
    data = yaml.load(file_data,Loader=yaml.FullLoader)
    return data

class TicToc:
    def __init__(self):
        self.t = None
        self.tic()
    def tic(self):
        self.t = time.time()
    def toc(self,msg=""):
        print("{}花费时间{}".format(msg,time.time()-self.t))





class OBSHelper():
    def __init__(self):

        self.obsClient = ObsClient(
                    access_key_id='XA18OYYMESRQ6ACL0ZAI',
                    secret_access_key='nNev8nWFMtUFUvDq4rIUyxSJYgLEssqKjdU56rvG',
                    server='https://obs.cn-north-4.myhuaweicloud.com'
            )
    # 使用访问OBS
    # 调用putFile接口上传对象到桶内
    def upload(self,tong='wx-all',obs_path="",file_path=""):
        resp = self.obsClient.putFile(tong, obs_path, file_path=file_path)
        if resp.status < 300:
            pass
            # 输出请求Id
            # print('requestId:', resp.requestId)
        else:
            # 输出错误码
            print('errorCode:', resp.errorCode)
            # 输出错误信息
            print('errorMessage:', resp.errorMessage)
        # 关闭obsClient

