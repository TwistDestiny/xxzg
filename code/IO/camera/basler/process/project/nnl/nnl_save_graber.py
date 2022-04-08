#######################################
import os
import sys

env_dist = os.environ
if "wx_home" in env_dist:
    sys.path.append(env_dist["wx_home"])
#######################################
print("0000")
from IO.camera.basler.process.save_graber import SaveBaslerCameras
import os
from concurrent.futures import ThreadPoolExecutor
from tools.wrapper import Safe

join = os.path.join
import json
from IO.camera.basler.process.img.nnl.process_img import process_img
import requests
import socket
import time


class NNLSaveGraber(SaveBaslerCameras):
    def __init__(self, begin_id, camera_ip_list, camera_config_list, save_root,
                 send_to_client=False,
                 client_ip="127.0.0.code",
                 client_port=12345,
                 send_prefix="02",
                 share_url="\\WIN-O5GVAHM4DSB\data",
                 save_format="jpg", server_url="",
                 image_height=2048, image_width=4096,
                 max_workers=15):
        super(NNLSaveGraber, self).__init__(begin_id, camera_ip_list, camera_config_list, save_root, save_format)
        self.image_width = image_width
        self.image_height = image_height
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        self.server_url = server_url

        self.send_to_client = send_to_client
        self.client_ip = client_ip
        self.client_port = client_port
        self.send_prefix = send_prefix
        self.src_img_share_url = share_url

        self.stop_speed = 0.2  # 小于这个转速停下

    def check_can_run(self):
        if self.speed is not None and self.speed <= self.stop_speed:
            time.sleep(0.3)
            return False
        else:
            return True

    def handle_img(self, image, camera_id, count):
        super(SaveBaslerCameras, self).handle_img(image, camera_id, count)

        light, dark = process_img(image, camera_id)
        info = dict(
            camera_id=camera_id + self.begin_id,
            edge_gap=0,
            count=count,
            day_info=self.day_info,
            trigger_info=self.trigger_info,
            right=self.image_width,
        )
        trigger_info = self.trigger_info
        day_info = self.day_info

        # save_folder = self.save_folder
        day = time.strftime("%Y-%m-%d", time.localtime())
        now = time.strftime("%H-%M", time.localtime())
        save_folder = os.path.join(self.save_root, day, now)

        light_folder = join(save_folder, "light")
        dark_folder = join(save_folder, "dark")
        if not os.path.exists(light_folder):
            os.makedirs(light_folder)
        if not os.path.exists(dark_folder):
            os.makedirs(dark_folder)

        light_name = join(save_folder, "light",
                          "{}_{:0>8d}.{}".format(self.begin_id + camera_id, count, self.save_format))
        dark_name = join(save_folder, "dark",
                         "{}_{:0>8d}.{}".format(self.begin_id + camera_id, count, self.save_format))
        share_name = "http://{}/i/{}/{}/{}/{}".format(
            self.src_img_share_url,
            day_info,
            trigger_info,
            "light",
            "{}_{:0>8d}.{}".format(self.begin_id + camera_id, count, self.save_format)
        )
        info["imgUrl"] = join(day_info, trigger_info,
                              "{}_{:0>8d}.{}".format(self.begin_id + camera_id, count, self.save_format))
        info["share_name"] = share_name
        info["http_name"] = "{}/i/{}/{}/{}/{}".format(
            self.src_img_share_url,
            day_info,
            trigger_info,
            "light",
            "{}_{:0>8d}.{}".format(self.begin_id + camera_id, count, self.save_format)
        )
        info['path'] = light_name
        info['path_dark'] = dark_name
        print(info)
        self.async_save_and_send(info, light, light_name, dark, dark_name)

    def async_save_and_send(self, info, light, light_name, dark, dark_name):
        self.thread_pool.submit(self.save_and_send, info, light, light_name, dark, dark_name)

    @Safe
    def save_and_send(self, info, light, light_name, dark, dark_name):
        self.save(light, light_name, dark, dark_name)
        self.send_server(info)
        if self.send_to_client:
            self.send_client(info["share_name"], info["camera_id"])

    def save(self, light, light_name, dark, dark_name):
        light.save(light_name)
        dark.save(dark_name)

    def async_send_client(self, share_name, camera_id):
        self.thread_pool.submit(self.send_client, share_name, camera_id)

    @Safe
    def send_client(self, share_name, camera_id):
        dict_ = dict(
            type=camera_id,
            imageLocation=share_name
        )
        send_s = json.dumps(dict_)
        send_s = self.send_prefix + send_s

        s = socket.socket()
        try:
            s.connect((self.client_ip, self.client_port))
            s.send(send_s.encode())
        except Exception as e:
            print("失去客户端{}：{} 的连接;错误{}".format(self.client_ip,
                                               self.client_port,
                                               repr(e)))

        s.close()

    def get_share_url_name(self, name):
        join(self.src_img_share_url, self.day_info, self.trigger_info)

    def send_server(self, info):
        values_json = json.dumps(
            dict(
                imgUrl=info["imgUrl"],  # 不带http://
                cameraId=info["camera_id"],
                # edgeGap=info["edge_gap"],
                # count=info["count"],
                # hasSteel=1 if info["has_steel"] else 0,
                # left=info["left"],
                # right=info["right"],
                absUrl=info["http_name"],
                width=4096,
                height=2048,  # 写死了要改
                camera_no=info["camera_id"],
                location=info['path'],
                image_serial_number=str(info["camera_id"]) + str(time.time()),
                location_dark=info["path_dark"],
            )
        )
        try:
            headers = {"Content-Type": "application/json"}
            req = requests.post("{}/api/data/image/push".format(self.server_url), data=values_json, headers=headers)
            print(time.strftime("%Y-%m-%d-%H-%M-%S",time.localtime()))
        except Exception as e:
            print("Post发送错误{}".format(repr(e)))
