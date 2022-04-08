import datetime
from tools.log import log

from enum import Enum
import time
import threading
import abc

class CMD(Enum):
    BEGIN = 0
    END = 1
    NC = 3  # 没有新指令

MAX_CAMERA = 32

class BaseCamera(threading.Thread):
    """
    模拟相机，真是相机必须继承的
    """
    def __init__(self):
        super(BaseCamera, self).__init__()

        # 辅助变量/状态量
        self.count = 0
        self._stop = True
        self.get_cmd_state = CMD.NC
        self.error_cnt = 0

        self.update_trigger_info()

        self.fps_channel_count_help = {}  #计数用的辅助

        # 监控输出用的变量
        self.export_temperatures = [0.0 for i in range(MAX_CAMERA)]
        self.fps_channel = [0.0 for i in range(MAX_CAMERA)]   # 1s有多少张图
        self.camera_state = [1.0 for i in range(MAX_CAMERA)]   # 可以看到相机的健康状态

        self.speed = None   # 辊道转速

    def check_can_run(self):
        # 暂停之类的交给checkcanrun
        return True
    def check_cmd(self):
        if self._stop:

            if self.get_cmd_state == CMD.BEGIN:
                # 停止中下达运行指令
                self.begin()
                return True
            else:
                # 停止中没有指令继续睡觉
                self.sleep_do()
                return False
        else:
            # 运行中下达停止指令
            if self.get_cmd_state == CMD.END:
                self.end()
                return False
            else:
                return True
    def sleep_do(self):
        time.sleep(0.3)
    def set_speed(self,speed):
        self.speed = speed
    def update_trigger_info(self):
        self.trigger_time = datetime.datetime.now()
        self.day_info = self.trigger_time.strftime("%Y-%m-%d")
        self.trigger_info = self.trigger_time.strftime("%H-%M-%S")
    def set_cmd(self, cmd):
        self.update_trigger_info()
        self.get_cmd_state = cmd

    def mkdir(self):
        self.update_trigger_info()
        return self._mkdir()
    def _mkdir(self):
        return ""
    # 分析到cmd背后的处理
    def begin(self):
        log.critical("set begin")
        if self._stop:
            self._stop = False
        self.count = 0
        self.error_cnt = 0

    def end(self):
        log.critical("set end")
        self._stop = True
        self.error_cnt = 0

    def safe_begin(self):
        """
        抓取失败的重新连接的begin,区别，count不清0
        :return:
        """
        log.critical("set safe_begin")
        if self._stop:
            self._stop = False
        # self.count = 0
        self.error_cnt = 0

    # 线程启动后运行的
    def run(self):
        '''
        record images and save in self.address_stamp
        :return:
        '''

        # self.ticToc = TicToc()
        # self.ticToc.tic()
        self.before_loop()
        while True:
            if not self.check_cmd():
                continue
            if not self.check_can_run():
                continue
            self.grab_image()
    def before_loop(self):
        pass
    def grab_image(self):
        # 主要循环 做抓图的
        pass
    # 处理图像
    @abc.abstractmethod
    def handle_img(self, image, camera_id, count):
        self.count_img(camera_id)
        """
        只接受灰度图像
        """
        pass

    def count_img(self,camera_id):
        """
        统计fps
        """
        if camera_id not in self.fps_channel_count_help:
            self.fps_channel_count_help[camera_id] = {
                "num":1,
                "trigger_time": time.time()
            }
        else:
            self.fps_channel_count_help[camera_id]["num"] = self.fps_channel_count_help[camera_id]["num"] + 1

    def get_fps(self):
        if self.fps_channel_count_help.__len__() == 0:
            return []
        else:
            now = time.time()
            fps = []
            for key in self.fps_channel_count_help:
                v = self.fps_channel_count_help[key]["num"]
                fps.append(
                    v/
                    (now-self.fps_channel_count_help[key]["trigger_time"])
                )
                self.fps_channel_count_help[key]["trigger_time"] = now
            return fps








if __name__ == "__main__":
    pass