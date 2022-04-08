
import os
import time
import cv2

from IO.camera.basler.base.grab import BaseCamera
from tools.config import config
join = os.path.join


# 也是基类必须要经过集成实现
class VisualCamera(BaseCamera):
    def __init__(self):
        super(VisualCamera, self).__init__()
        visual_config = config["camera_group"]["visual"]
        root = visual_config["visual_img_root"]
        self.cycle_fps = visual_config["cycle_fps"]
        self.img_list = [join(root, i) for i in os.listdir(root)]
        self.i = 0


    def run(self):

        while True:
            idx = 0
            time.sleep(1 / self.cycle_fps)
            self.i = self.i + 1
            img =  cv2.imread(self.img_list[self.i % len(self.img_list)],0)
            self.handle_img(img,idx%4,self.count)
            self.count = self.count + 1
            self.camera_state[idx] = 1.0
            idx = idx + 1
            if idx >= 4:
                idx = 0
    def handle_img(self, image, camera_id, count):
        super(VisualCamera, self).handle_img(image, camera_id, count)