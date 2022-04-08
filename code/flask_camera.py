#######################################
import os
import sys


env_dist = os.environ
if "wx_home" in env_dist:
    sys.path.append(env_dist["wx_home"])
#######################################

import logging

from flask import Flask,Response
from IO.camera.basler.base.grab import CMD
import json
from tools.MetricsBase import MetricBase
from tools.config import config
from flask import request
app=Flask(__name__)



class Metricer(MetricBase):
    def __init__(self):
        super(Metricer, self).__init__()
        self.register("queue_max_len", "最大队列长度")
        self.register("queue_max_len_index", "最大队列序号")
        # 代码没用了
        for i in range(config["camera_group"]["TCPSender"]["thread_num"]):
            self.register("queue_{}".format(i), "{}号线程队列长度".format(i))
        ###
        for i in range(len(config["camera_group"]["camera_config_list"])):
            self.register("T_{}".format(i), "{}号相机温度".format(i))
            self.register("fps_{}".format(i), "{}号fps".format(i))
            self.register("camera_state_{}".format(i), "{}号状态".format(i))
    def update(self):

        max_q_idx = 0
        max_q = 0
        if hasattr(camera,"server_list"):
            for i in range(config["camera_group"]["TCPSender"]["thread_num"]):
                self.set("queue_{}".format(i),camera.server_list[i].queue.qsize())
                if max_q <= camera.server_list[i].queue.qsize():
                    max_q = camera.server_list[i].queue.qsize()
                    max_q_idx = i
            self.set("queue_max_len", max_q)
            self.set("queue_max_len_index", max_q_idx)
        if config["camera_group"]["mode"] == "http_send_camera":

            size = camera.get_queue_size()
            self.set("queue_max_len",size)
            self.set("queue_max_len_index", 0)

        fps = camera.get_fps()
        for i in range(len(config["camera_group"]["camera_config_list"])):
            self.set("T_{}".format(i),camera.export_temperatures[i])
            self.set("camera_state_{}".format(i), camera.camera_state[i])
            if i  < len(fps):
                self.set("fps_{}".format(i), fps[i])


metricer = Metricer()
@app.route("/metrics")
def metrics():
    return Response(metricer.get_html_context(),
                    mimetype="text/plain")




@app.route('/begin',methods=['GET'])
def begin():
    camera.set_cmd(CMD.BEGIN)
    print("begin")
    return json.dumps(dict(
        code="200",
        data=True,
        message='SUCCESS'
    ), ensure_ascii=False)





@app.route('/end',methods=['GET'])
def end():
    # metricsValue.request_state.set(0)
    camera.set_cmd(CMD.END)
    print("end")
    return json.dumps(dict(
        code="200",
        data=True,
        message='SUCCESS'
    ), ensure_ascii=False)


@app.route("/speed",methods=['GET','POST'])
def set_speed():
    data = request.get_json()
    if data:
        speed = data["speed"]
        camera.set_speed(speed)
    return ""

if __name__=='__main__':

    if config["camera_group"]["mode"] == "tcp_visual":
        from IO.camera.basler.process.tcp_graber import TcpVisualCameras
        camera = TcpVisualCameras()
    elif config["camera_group"]["mode"] == "tcp_basler":
        from IO.camera.basler.process.tcp_graber import TcpBaslerCameras
        camera = TcpBaslerCameras(
            config["camera_group"]["begin_id"],
            config["camera_group"]["camera_ip_list"],
            config["camera_group"]["camera_config_list"],
        )
    elif config["camera_group"]["mode"] == "nnl_save_basler":
        from IO.camera.basler.process.project.nnl.nnl_save_graber import NNLSaveGraber
        camera = NNLSaveGraber(
            config["camera_group"]["begin_id"],
            config["camera_group"]["camera_ip_list"],
            config["camera_group"]["camera_config_list"],
            config["camera_group"]["save_root"],

            send_to_client= config["camera_group"]["send_to_client"],
            client_ip=config["workshop_cs"]["bind_ip"],
            client_port=config["workshop_cs"]["bind_port"],
            send_prefix=config["workshop_cs"]["send_prefix"],
            share_url=config["camera_group"]["share_url"],

            server_url=config["sp01"]["server_url"],
            image_height=config["image"]["height"],
            image_width=config["image"]["width"],
        )
    elif config["camera_group"]["mode"] == "nnl_visual_save_basler":
        from IO.camera.basler.process.project.nnl.nnl_visual_save_graber import NNLViusalSaveGraber
        camera = NNLViusalSaveGraber(
            config["camera_group"]["begin_id"],
            [],
            [],
            config["camera_group"]["save_root"],

            send_to_client= config["camera_group"]["send_to_client"],
            client_ip=config["workshop_cs"]["bind_ip"],
            client_port=config["workshop_cs"]["bind_port"],
            send_prefix=config["workshop_cs"]["send_prefix"],
            share_url=config["camera_group"]["share_url"],

            server_url=config["sp01"]["server_url"],
            image_height=config["image"]["height"],
            image_width=config["image"]["width"],
        )
    elif config["camera_group"]["mode"] == "http_send_camera":
        from IO.camera.basler.process.project.bangcai3.HttpSendCamera import HttpSendCamera
        camera = HttpSendCamera(
            config["camera_group"]["begin_id"],
            config["camera_group"]["camera_ip_list"],
            config["camera_group"]["camera_config_list"],
            send_url=config["camera_group"]["http"]["send_url"],
            send_thread=config["camera_group"]["http"]["send_thread_num"],
            gkj_process_ratio=config["camera_group"]["http"]["gkj_process_ratio"]

        )
    else:
        from IO.camera.basler.process.save_graber import SaveBaslerCameras
        camera = SaveBaslerCameras(
            config["camera_group"]["begin_id"],
            config["camera_group"]["camera_ip_list"],
            config["camera_group"]["camera_config_list"],
            config["camera_group"]["save_root"]
        )

    camera.start()
    flask_log = logging.getLogger('werkzeug')
    flask_log.disabled = True
    app.debug=False
    app.run(host=config["camera_group"]["bind_ip"],port=config["camera_group"]["bind_port"])
