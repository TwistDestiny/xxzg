
import os
from tools.utils import parseYaml
import os
import sys
join = os.path.join

def get_config(env="dev",name="gkj01"):
    root = os.path.dirname(os.path.dirname(__file__))
    config = parseYaml(join(root,"resource","static","config","{}.yaml".format(env)))
    config["name"] = name
    config["mode"] = env
    if name in config:
        for key in config[name]:
            config[key] = config[name][key]
    return config