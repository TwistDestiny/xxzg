import urllib
import numpy as np
import cv2
def get_mat_from_url(imageUrl):
    imageUrl = imageUrl.replace("\\", "/")
    if "http://" not in imageUrl:
        imageUrl = "http://{}".format(imageUrl)
    response = urllib.request.urlopen(imageUrl)
    img_array = np.array(bytearray(response.read()), dtype=np.uint8)
    img = cv2.imdecode(img_array, -1)
    return img