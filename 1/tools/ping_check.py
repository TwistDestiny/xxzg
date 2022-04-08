import os
from threading import Thread
import time
class Checker(Thread):
    def __init__(self,ip_list):
        super(Checker, self).__init__()
        self.ip_list = ip_list
    def run(self):
        while True:
            try:
                for ip in self.ip_list:
                    check = check_ping(ip)
                    if not check:
                        print("ping {} error".format(ip))
                        self.handle(ip)
                    else:
                        print("ping {} success".format(ip))
            except Exception as e:
                print(repr(e))
            time.sleep(3)
    def handle(self,ip):
        pass

import subprocess, platform
def check_ping(sHost):
    try:
        output = subprocess.check_output("ping -{} 1 {}".format('n' if platform.system().lower()=="windows" else 'c', sHost), shell=True)

    except Exception as e:
        return False

    return True
