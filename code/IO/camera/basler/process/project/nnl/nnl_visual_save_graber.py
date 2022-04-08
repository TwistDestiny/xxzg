#######################################
import os
import sys

env_dist = os.environ
if "wx_home" in env_dist:
    sys.path.append(env_dist["wx_home"])
#######################################

from IO.camera.basler.process.project.nnl.nnl_save_graber import NNLSaveGraber
import os

join = os.path.join
import time
import cv2
import numpy as np
class NNLViusalSaveGraber(NNLSaveGraber):
    def __init__(self, begin_id, camera_ip_list, camera_config_list, save_root,
                 send_to_client=False,
                 client_ip="127.0.0.code",
                 client_port=12345,
                 send_prefix="02",
                 share_url="\\WIN-O5GVAHM4DSB\data",
                 save_format="jpg",server_url="",
                 image_height=2048,image_width=4096,
                 max_workers=15):
        super(NNLViusalSaveGraber, self).__init__(
            begin_id, camera_ip_list, camera_config_list, save_root,
            send_to_client,
            client_ip,
            client_port,
            send_prefix,
            share_url,
            save_format,
            server_url,
            image_height,
            image_width,
            max_workers
        )
        # super(NNLViusalSaveGraber, self).__init__(begin_id, camera_ip_list, camera_config_list, save_root, save_format)


    # 分析到cmd背后的处理
    def begin(self):
        # log.critical("set begin")
        if self._stop:
            self._stop = False
        self.count = 0
        self.error_cnt = 0

    def end(self):
        # log.critical("set end")
        self._stop = True
        self.error_cnt = 0

    def run(self):
        self.cycle_fps = 1.2*4 # fps值大小
        self.img_root = r"D:\data\dst"
        self.light_list = [join(self.img_root,"light",name) for name in os.listdir(join(self.img_root,"light"))]
        self.dark_list = [join(self.img_root,"dark",name) for name in os.listdir(join(self.img_root,"dark"))]
        self.i = 0
        idx = self.begin_id
        while True:


            if not self.check_cmd():
                continue

            time.sleep(1 / self.cycle_fps)
            self.i = self.i + 1
            img0 = cv2.imread(self.light_list[self.i % len(self.light_list)], 0)
            img1 = cv2.imread(self.dark_list[self.i % len(self.dark_list)], 0)
            img =  np.zeros((4096,4096))
            img0 = cv2.resize(img0,(4096,2048))
            img1 = cv2.resize(img1, (4096, 2048))
            print(img[0::2, :].shape,img.shape)
            img[0::2, :] = img0
            img[1::2, :] =img1
            img = img.astype(np.uint8)
            self.handle_img(img, idx % 4, self.count)
            self.count = self.count + 1
            self.camera_state[idx] = 1.0
            idx = idx + 1
            if idx >= self.begin_id +4 :
                idx = self.begin_id


