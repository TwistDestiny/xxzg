import cv2

from IO.camera.basler.process.img.bangcai3.edge_help import get_border
import time
import functools
import os
from tools.config import config


join = os.path.join
os.makedirs(config["edge_root"],exist_ok=True)
# class ImageProcessor():
#
#     def __init__(self):
#         self.state = False
#         self.last_state = True
def clock(func):
    """this is outer clock function"""

    @functools.wraps(func)  # --> 4
    def clocked(*args, **kwargs):  # -- 1
        """this is inner clocked function"""
        start_time = time.time()
        result = func(*args, **kwargs)  # --> 2
        time_cost = time.time() - start_time
        print(func.__name__ + " func time_cost -> {}".format(time_cost))
        return result
    return clocked  # --> 3
# @clock
def process_img(image,camera_id):
    """
    :param image: np图像
    :param camera_id: 相机号
    :return: 图像,是否有钢，left,right
    """
    if config["save_edge_source"]:
        cv2.imwrite(join(config["edge_root"], "{}_{}.jpg".format(int(time.time() * 1000), camera_id)), image)
    # print(image.shape,image.dtype,threading.currentThread())
    border = get_border(image)
    # print("border=",border)
    has_steel = True
    if border is None:
        has_steel = False
        return image,has_steel,None,None
    else:
        # 先不增加去边算法
        # image[:,:border[0]] = 0
        # image[:,border[1]:] = 1
        left,right = int(border[0]),int(border[1])
        if right - left > 100:
            # image[:, :left] = 0
            # image[:,right:] = 0
            width = right - left
            width15 = int(width*config["border_ratio"])
            left = left + width15
            right = right - width15
            # image = image[:,left:right]
        else:
            has_steel = False
            # cv2.imwrite(join(config["edge_save"],"{}_{}.jpg".format(int(time.time()*1000),camera_id)),image)
        return image,has_steel,left,right