"""
检查是西门子的rack和slot
"""
from IO.snapBeanInterface import SnapBeanInterface

class SnapBean(SnapBeanInterface):
    """
    处理PLC读写的组件
    """
    def __init__(self,trigger):
        super(SnapBean,self).__init__()
        self.init_data(trigger)

for rack in range(0,10):
    for slot in range(0,10):
        trigger = dict(
            ip="10.15.76.200",
            slot=slot,
            rack=rack,
            dbnumber=4,
            start=4,
            amount=4,
            unpack_code=">f",
            pack_code=">f",
        )
        snapBean = SnapBean(trigger)
        for i in range(2):
            try:
                snapBean.read()
                print("right slot={} rack={}".format(slot,rack))
                exit(1)
            except Exception as e:
                pass
            print("slot={} rack={} failed".format(slot,rack))
