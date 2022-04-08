import prometheus_client
from prometheus_client import Gauge
import abc
class MetricBase():
    def __init__(self):
        self.value_dict = {}
    
    @abc.abstractmethod
    def update(self):
        # self.value_dict[name].set(code)
        pass
    def register(self,name,meta):
        """
        name 变量名称
        meta 变量注释
        """
        self.value_dict[name] = Gauge(name, meta)
    def set(self,name,value):
        """
        value为浮点数
        """
        self.value_dict[name].set(value)
    def get_html_context(self):
        self.update()
        r = b''
        for key in self.value_dict:
            r = r + prometheus_client.generate_latest(self.value_dict[key])
        return r

if __name__ == "__main__":
    class Metricer(MetricBase):
        def __init__(self):
            super(Metricer,self).__init__()
            self.register("grade","考试成绩")
        def update(self):
            self.set("grade",50)