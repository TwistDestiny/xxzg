import os
from PIL import Image

from IO.camera.basler.base.grab import CMD, BaseCamera
from IO.camera.basler.source.basler_camera import BaslerCameras

join = os.path.join


class SaveBaseCameras(BaseCamera):
    def __init__(self, save_root, save_format="jpg"):
        super(SaveBaseCameras, self).__init__()
        self.save_root = save_root
        self.save_format = save_format
        self.save_folder = self.mkdir()

    def begin(self):
        super(SaveBaseCameras, self).begin()
        self.save_folder = self._mkdir()

    def set_cmd(self, cmd):
        super(SaveBaseCameras, self).set_cmd(cmd)
        if cmd == CMD.BEGIN:
            self.save_folder = self._mkdir()

    def _mkdir(self):
        dirname = join(self.save_root, self.day_info, self.trigger_info)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        return dirname


class SaveBaslerCameras(BaslerCameras):
    """
    把图片保存在本地
    """

    def __init__(self, begin_id, camera_ip_list, camera_config_list, save_root, save_format="jpg"):
        super(SaveBaslerCameras, self).__init__(begin_id, camera_ip_list, camera_config_list)
        self.save_root = save_root
        self.save_format = save_format
        # self.save_folder = self.mkdir()

    def begin(self):
        super(SaveBaslerCameras, self).begin()
        # self.save_folder = self._mkdir()

    def set_cmd(self, cmd):
        super(SaveBaslerCameras, self).set_cmd(cmd)
        # if cmd == CMD.BEGIN:
        #     self.save_folder = self._mkdir()

    def _mkdir(self):
        dirname = join(self.save_root, self.day_info, self.trigger_info)
        if not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)
        return dirname

    def handle_img(self, image, camera_id, count):
        super(SaveBaslerCameras, self).handle_img(image, camera_id, count)

        image = Image.fromarray(image)
        save_name = join(self.save_folder, "{}_{}.{}".format(self.begin_id + camera_id, count, self.save_format))
        image.save(save_name)


def route_grab():
    from tools.config import config
    camera = SaveBaslerCameras(
        begin_id=config["camera_group"]["begin_id"],
        camera_ip_list=config["camera_group"]["camera_ip_list"],
        camera_config_list=config["camera_group"]["camera_config_list"],
        save_root=config["camera_group"]["save_root"]
    )
    camera.start()
    import time
    from IO.camera.basler.base.grab import CMD
    while True:
        time.sleep(2)
        camera.set_cmd(CMD.BEGIN)
        time.sleep(10)
        camera.set_cmd(CMD.END)


if __name__ == "__main__":
    pass
