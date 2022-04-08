import numpy as np
import cv2
from PIL import Image
from PIL import ImageDraw
from tools.config import config
class EdgeCalc():
    def __init__(self):
        self.p = 0.1
    def find_edge(self,image):
        assert len(image.shape) == 2
        sum_image = np.mean(image, axis=0)
        integer_image = np.zeros_like(sum_image)
        integer_mean_image = np.zeros_like(sum_image)
        for i, is_ in enumerate(sum_image):
            if i == 0:
                integer_image[0] = is_
            else:
                integer_image[i] = integer_image[i - 1] + is_

            integer_mean_image[i] = integer_image[i] / (i + 1)

        sub_image_0 = integer_image[:-1]
        sub_image_1 = integer_image[1:]
        delta = np.abs(sub_image_1 - sub_image_0)
        mean_delta = np.max(delta)
        indices = np.where(delta > self.p * mean_delta)[0]

        edge = None
        if len(indices) > 0:
            edge = indices[0]
            im_h, im_w = image.shape
            image_mean = np.mean(image)
            edge = indices[0]
            if edge == 0:
                edge = 1
            sub_image_mean = np.mean(image[:im_h, :edge])
            if sub_image_mean > 10:
                edge = None
        return edge
    def get_calc(self,light,dark):
        edge_gap = 0
        try:
            edge = self.find_edge(np.array(light).astype(np.uint8))
            if edge == None:
                return None
            else:
                edge_gap = edge
                return edge_gap
        except Exception as e:
            print(repr(e))
        return edge_gap





class EdgeHelper(EdgeCalc):
    def __init__(self):
        super(EdgeHelper,self).__init__()
        self.clear()

    def clear(self):
        self.edge = 0

        self.in_loop_find_edge = False   #循环中是否找到edge
    def get_gap(self,camera_idx,light,dark):
        if camera_idx == 0:
            # 从0开始找
            self.clear()

        if self.in_loop_find_edge:
            # 这组循环中已经找到了
            return self.edge
        edge = self.get_calc(light,dark)
        if edge == None:
            return 0  # 没找到钢
        else:
            self.in_loop_find_edge = True
            self.edge = int(edge) + camera_idx * config["image"]["width"]
            return self.edge
