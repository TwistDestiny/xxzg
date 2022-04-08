from concurrent.futures.thread import ThreadPoolExecutor

from IO.camera.basler.process.img.bangcai3.process_img import process_img
from IO.camera.basler.source.basler_camera import BaslerCameras

from threading import Thread
from queue import Queue

from tools.cv2base64 import image_to_base64
from  tools.wrapper import SAFE
import time
import requests
import json
# import grequests
class HttpSender():
    def __init__(self,send_url,send_thread=5,sleep_ms=150):
        super(HttpSender, self).__init__()
        self.send_url = send_url
        self.queue = Queue()

        self.send_thread = send_thread
        self.threadpool = ThreadPoolExecutor(max_workers=self.send_thread)
        print("队列长度{}".format(self.threadpool._work_queue.qsize()))
        self.sleep_ms = sleep_ms
    # def run(self):
    #     while True:
    #         self.loop_func()
    # @SAFE
    # def loop_func(self):
    #     if self.queue.qsize() > 0:
    #         c = self.queue.get()
    #         self.threadpool.submit(self.send_img,c[0],c[1])
    #
    #     else:
    #         time.sleep(self.sleep_ms/1000)

    # def put(self,img,info):
    #     self.queue.put((img,info))

    def async_send_img(self,img,info):
        self.threadpool.submit(self.send_img,image_to_base64(img),info)
        print("队列长度{}".format(self.threadpool._work_queue.qsize()))
    @SAFE
    def send_img(self,img_base64,info):
        data = {"data": info, "img": img_base64}
        response = requests.get(self.send_url, json=json.dumps(data))

class HttpSendCamera(BaslerCameras):
    def __init__(self,begin_id,camera_ip_list,camera_config_list,send_url,send_thread):
        super(HttpSendCamera,self).__init__(begin_id,camera_ip_list,camera_config_list)
        self.calc_percent = 0.5  # 有多少是在工控机上做计算
        self.sender = HttpSender(send_url=send_url,send_thread=send_thread)

    def handle_img(self,image,camera_id,count):
        super(HttpSendCamera, self).handle_img(image, camera_id, count)
        has_process = False
        has_process, has_steel, image, left, right = self.qiebian_mod(camera_id, count, has_process, image)
        info = dict(
            camera_id=camera_id + self.begin_id,
            edge_gap=0,
            count=count,
            day_info=self.day_info,
            trigger_info=self.trigger_info,
            has_steel=has_steel,
            left=left,
            right=right,
            has_process=has_process
        )
        self.send(image,info)

    def qiebian_mod(self, camera_id, count, has_process, image):
        if count % 10 < self.calc_percent * 10:
            image, has_steel, left, right = process_img(image, camera_id)
            has_process = True
        else:
            image, has_steel, left, right = image, True, 0, 1024
        return has_process, has_steel, image, left, right

    def send(self,image,info):
        print("info",info)
        self.sender.async_send_img(image,info)