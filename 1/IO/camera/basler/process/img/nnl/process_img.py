from PIL import Image
from IO.camera.basler.process.img.nnl.edge_help import EdgeHelper
edgeHelper = EdgeHelper()

def process_img(image,camera_id):
    even = image[::2, :]
    odd = image[1::2, :]
    even_mean = even.mean()
    odd_mean = odd.mean()

    if even_mean >= odd_mean:
        light = Image.fromarray(even)
        dark = Image.fromarray(odd)
    else:
        dark = Image.fromarray(even)
        light = Image.fromarray(odd)
    edge = edgeHelper.get_gap(camera_id,light=light,dark=dark)
    has_steel = True if edge !=0 else False
    return light,dark,has_steel,edge