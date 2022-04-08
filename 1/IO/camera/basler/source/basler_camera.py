from IO.camera.basler.base.grab import BaseCamera
from pypylon import pylon
import numpy as np
from pypylon.genicam import LogicalErrorException, RuntimeException

from tools.log import log
from tools.utils import ex
from tools.error_handle import errorHandle
import time
import os

from tools.wrapper import SAFE


class BaslerCameras(BaseCamera):
    """
    basler相机
    """
    def __init__(self, begin_id,camera_ip_list,camera_config_list):
        # 复杂的业务交给子类去做
        # 主类保证相机运行的高可用性，并暴露一些好用的接口
        super(BaslerCameras, self).__init__()

        self.begin_id = begin_id
        self.ip_list = camera_ip_list
        self.camera_config_list = camera_config_list

        # 辅助工具
        self.converter = pylon.ImageFormatConverter()
        self.converter.OutputPixelFormat = pylon.PixelType_BGR8packed
        self.converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

        # 辅助变量
        self.grab_lock = False  # grab_lock 是开始grab和结束grab的保护lock 确保不会被两次startgrabing
        self.temperature_cnt = 0

        self.camera_num = len(camera_ip_list)
        # self.export_temperatures = [0.0 for i in range(self.camera_num)]
        # self.camera_state = [1.0 for i in range(self.camera_num)]    # 可以看到相机的健康状态
        self.cameras = []
        self.init_cameras()



    def start_grab(self):
        """
        相机开启取流模式
        """
        log.info("start grab")
        if not self.grab_lock:
            for index,camera in enumerate(self.cameras):
                try:
                    camera.StartGrabbing()
                except Exception as e:
                    errorHandle.error("{}号相机不能StartGrabbing".format(index))
                    errorHandle.error(e)
            self.grab_lock = True
    def stop_grab(self):
        """
        相机关闭取流模式
        """
        log.info("stop grab")
        if self.grab_lock:
            for camera in self.cameras:
                camera.StopGrabbing()
            self.grab_lock = False

    def begin(self):
        super(BaslerCameras, self).begin()
        self.start_grab()

    def end(self):
        super(BaslerCameras, self).end()
        self.stop_grab()

    def safe_begin(self):
        """
        抓取失败的重新连接的begin,区别，count不清0
        :return:
        """
        super(BaslerCameras, self).safe_begin()
        self.start_grab()


    def init_cameras(self):
        '''
        先确定图像数后，再根据图像的连接数量 给每个相机的配置文件加载。
        :return:  cameras
        '''
        log.info("init cameras")
        try:

            for i in range(self.camera_num):
                factory = pylon.TlFactory.GetInstance()
                ptl = factory.CreateTl('BaslerGigE')
                empty_camera_info = ptl.CreateDeviceInfo()
                empty_camera_info.SetPropertyValue('IpAddress', self.ip_list[i])
                camera_device = factory.CreateDevice(empty_camera_info)
                camera = pylon.InstantCamera(camera_device)
                camera.Open()
                log.info("打开相机{}成功".format(self.begin_id + i))
                if not os.path.exists(self.camera_config_list[i]):
                    raise Exception("加载{}相机失败，配置文件{}不存在".format(i,self.camera_config_list[i]))
                pylon.FeaturePersistence.Load(self.camera_config_list[i], camera.GetNodeMap(), True)
                self.cameras.append(camera)
                log.info("初始化相机{}成功".format(self.begin_id+i))
            log.info("初始化{}个相机成功".format(self.camera_num))
            self.update_temperature()
        except Exception as e:
            log.info("初始化相机失败")
            errorHandle.error(e)
            log.info("退出程序")
            ex()

    def close_camera(self):
        log.info("close camea")
        self.end()
        for idx,camera in enumerate(self.cameras):
            try:
                camera.DetachDevice()
                camera.Close()
            except Exception as e:
                errorHandle.error("{}号相机关闭失败{}".format(idx,repr(e)),send_mail=False)


    def get_state(self):
        for idx,cam in enumerate(self.cameras):
            print("###第{}台相机###".format(idx))
            print("TriggerSource", cam.TriggerSource.GetValue())
            print("TriggerMode", cam.TriggerMode.GetValue())
            print("AcquisitionMode", cam.AcquisitionMode.GetValue())

    def load_fps(self):
        # if hasattr(self.cameras, "__len__"):
        for sub_i, cam in enumerate(self.cameras):
            self.cameras[sub_i].Open()
            log.info("pfs = {},{}".format(self.camera_config_list[sub_i], sub_i))
            pylon.FeaturePersistence.Load(self.camera_config_list[sub_i], self.cameras[sub_i].GetNodeMap(), True)
            self.cameras[sub_i].Close()





    def grab_image(self):
        try:
            grab_success = True
            for camera_id in range(len(self.cameras)):
                try:
                    result = self.cameras[camera_id].RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
                    success = result.GrabSucceeded()
                    self.camera_state[camera_id] = 1.0
                    """
                    抓取图像期间若遇到 连接错误 抓取错误的问题则：
                        重新连接-重新抓取,count 不清零

                    """
                    self.error_cnt = 0
                except (LogicalErrorException, RuntimeException, IndexError) as e:
                    self.camera_state[camera_id] = -2.0
                    errorHandle.error("相机{}异常:{}".format(camera_id, repr(e)))
                    self.restart_cameta()
                    break

                except Exception as e:
                    # self.error_cnt = self.error_cnt + 1
                    self.camera_state[camera_id] = -1.0
                    log.error("相機{}超时:{}".format(camera_id ,repr(e)))
                    grab_success = False
                    break
                if success:
                    image = self.converter.Convert(result)
                    image = image.GetArray()
                    result.Release()
                    image = image[:, :, 0].astype(np.uint8)
                    self.handle_img(image, camera_id, self.count)
                else:
                    grab_success = False
            if grab_success == False:
                return

            if grab_success:
                self.count = self.count + 1
                if self.count % 25 == 0:
                    self.update_temperature()

            if self.error_cnt >= 50:
                if not self._stop:
                    self.restart_cameta()

        except Exception as e:
            errorHandle.error(e)
    def sleep_do(self):
        # 停止中没有指令继续睡觉
        self.temperature_cnt = self.temperature_cnt + 1
        if self.temperature_cnt >= 15:
            self.update_temperature()
            self.temperature_cnt = 0
        time.sleep(0.3)
    @SAFE
    def update_temperature(self):
        for i in range(self.camera_num):
            T = self.cameras[i].TemperatureAbs()
            state = self.cameras[i].TemperatureState.GetValue()
            self.export_temperatures[i] = T
            if state != "Ok":
                errorHandle.error("{}号相机温度={},状态{}".format(i,T,state),send_mail=False)
                self.reset_camera(i)
    def restart_cameta(self):
        """
        相机断线->重连->startgrabbing
        """
        log.info("restart")
        self.error_cnt = self.error_cnt + 1
        self.close_camera()
        self.init_cameras()
        self.safe_begin()


    def handle_img(self,image,camera_id,count):
        super(BaslerCameras, self).handle_img(image,camera_id,count)
    def reset_camera(self,idx):
        """
        超温后reset
        """
        log.info("重启{}号相机".format(idx))
        self.cameras[idx].DeviceReset()
        time.sleep(10)
        self.restart_cameta()