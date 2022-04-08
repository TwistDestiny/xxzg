from threading import Thread
import time
from tools.log import log
import time


cnt_dict = {}
tic_dict = {}
def CNT(func):


    def wrapper(*args, **kwargs):

        ret = func(*args, **kwargs)

        if func.__name__ in cnt_dict:
            cnt_dict[func.__name__] = cnt_dict[func.__name__] + 1
            if cnt_dict[func.__name__] % 100 == 0:
                toc = time.time()
                tic = tic_dict[func.__name__]
                tic_dict[func.__name__] = toc
                print("函数{}运行100次时间{}".format(func.__name__, toc - tic))
        else:
            cnt_dict[func.__name__] = 0
            tic_dict[func.__name__] = time.time()

        return ret
    return wrapper
def TicToc(func):
    def wrapper(*args, **kwargs):
        tic = time.time()
        ret = func(*args, **kwargs)
        toc = time.time()
        print("函数{}运行时间{}".format(func.__name__,toc-tic))
        return ret
    return wrapper
def Async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()

    return wrapper

def Safe(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args,**kwargs)
        except Exception as e:
            log.info("函数{}运行错误：{}".format(func.__name__,repr(e)))

    return wrapper


def SAFE(func):
    # 只有trycatch 不发邮件
    def wrapper(*args, **kwargs):
        try:
            return func(*args,**kwargs)
        except Exception as e:
            log.info("函数{}运行错误：{}".format(func.__name__,repr(e)))

    return wrapper











"""
用例子
"""
class T():
    @Async
    @Safe
    def async_func(self,i):
        print("sleeping")
        time.sleep(i)
        raise Exception("hello")
        print("sleeping over")

def main():
    T().async_func(2)
    print("func emit")
if __name__ == "__main__":
    main()