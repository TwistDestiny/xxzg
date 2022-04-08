from threading import Thread

from tools.log import log
from tools.config import config
import json
import requests
import traceback

def Async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()

    return wrapper
class ErrorHandle():
    def __init__(self,alert_url):
        self.alert_url = alert_url

    @Async
    def post_error_msg(self,send_out=True,error_s="",send_mail=True):
        if send_out and "lc_meta" in config:
            data = dict()
            data["lc_meta"] = config["lc_meta"]
            data["msg"] = error_s
            data["send_mail"] = send_mail
            data_json = json.dumps(data)
            try:
                requests.post(self.alert_url, data_json)
            except Exception as e:
                log.error(e,exc_info=1)

    def error(self,e,send_out=True,send_mail=True):
        if not isinstance(e,str):
            error_s = "{}".format(traceback.format_exc())
        else:
            error_s = "{}".format(e)
        try:
            log.error(error_s)
        except Exception as e:
            print(repr(e))
        if "send_out" in config and not config["send_out"]:
            return
        self.post_error_msg(send_out=send_out,error_s=error_s,send_mail=send_mail)
        # print(repr(e))



errorHandle = ErrorHandle(config["alert_url"] if "alert_url" in config else "" )

if __name__ == "__main__":
    errorHandle.error("没啥信息")
    import time
    time.sleep(3)