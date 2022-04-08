"""
使用socket把图像传递走
"""

from IO.camera.basler.source.basler_camera import  BaslerCameras
from IO.camera.basler.process.img.bangcai3.process_img import process_img
from tools.config import config
from IO.camera.basler.source.visual_camera import VisualCamera
from IO.TCPSend.ts import Server

class TcpVisualCameras(VisualCamera):
    """
    图片发出去
    """

    def __init__(self):
        super(TcpVisualCameras, self).__init__()
        tcp_config = config["camera_group"]["TCPSender"]
        self.server_list = [
            Server(
                tcp_config["bind_ip"],
                tcp_config["bind_port_begin"] + i,
                tcp_config["name"] + "_" + str(i),
                tcp_config["num_to_cache"],
                tcp_config["num_to_send"],
                tcp_config["buffer_size"],
                tcp_config["thread_sleep_ms"],
            )
            for i in range(config["camera_group"]["TCPSender"]["thread_num"])
        ]
        for i in range(config["camera_group"]["TCPSender"]["thread_num"]):
            self.server_list[i].start()
        self.server_idx = 0
        self.block = tcp_config["block"]
    def handle_img(self,image,camera_id,count):
        super(TcpVisualCameras, self).handle_img(image,camera_id,count)
        image, has_steel, left, right = process_img(image, camera_id)
        info = dict(
            camera_id=camera_id,
            edge_gap=0,
            count=count,
            day_info=self.day_info,
            trigger_info=self.trigger_info,
            has_steel=has_steel,
            left=left,
            right=right,
        )
        self.send(image,info)
    def send(self,image,info):
        if self.server_idx >= self.server_list.__len__():
            self.server_idx = 0
        self.server_list[self.server_idx].put_image_and_info(image,info,block=self.block)
        self.server_idx = self.server_idx + 1




class TcpBaslerCameras(BaslerCameras):
    """
    图片发出去
    """

    def __init__(self, begin_id, camera_ip_list, camera_config_list):
        super(TcpBaslerCameras, self).__init__(begin_id, camera_ip_list, camera_config_list)
        tcp_config = config["camera_group"]["TCPSender"]
        self.server_list = [
            Server(
                tcp_config["bind_ip"],
                tcp_config["bind_port_begin"] + i,
                tcp_config["name"] + "_" + str(i),
                tcp_config["num_to_cache"],
                tcp_config["num_to_send"],
                tcp_config["buffer_size"],
                tcp_config["thread_sleep_ms"],
            )
            for i in range(tcp_config["thread_num"])
        ]
        for i in range(tcp_config["thread_num"]):
            self.server_list[i].start()
        self.server_idx = 0
        self.block = tcp_config["block"]
    def handle_img(self,image,camera_id,count):
        super(TcpBaslerCameras, self).handle_img(image,camera_id,count)
        image, has_steel, left, right = process_img(image, camera_id)
        info = dict(
            camera_id=camera_id+self.begin_id,
            edge_gap=0,
            count=count,
            day_info=self.day_info,
            trigger_info=self.trigger_info,
            has_steel=has_steel,
            left=left,
            right=right,
        )
        self.send(image,info)
    def send(self,image,info):
        if self.server_idx >= self.server_list.__len__():
            self.server_idx = 0
        self.server_list[self.server_idx].put_image_and_info(image, info, block=self.block)
        self.server_idx = self.server_idx + 1
