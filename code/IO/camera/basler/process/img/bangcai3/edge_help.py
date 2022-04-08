from keras.models import load_model
import keras.backend as K
import tensorflow as tf
import numpy as np
import glob,os
import cv2
from PIL import Image
from tensorflow.python.keras.backend import set_session

from tools.wrapper import TicToc, CNT

os.environ["CUDA_VISIBLE_DEVICES"]="-code"

def model_loss(y_true, y_pred):
    positive_mask = K.switch(K.greater(y_true,0.0),  K.ones_like(y_true), K.zeros_like(y_true))
    negitive_mask = K.switch(K.equal(y_true,0.0), K.ones_like(y_true), K.zeros_like(y_true))
    pos_loss = positive_mask * K.pow(K.stop_gradient(1 - y_pred), 2) *  K.binary_crossentropy(y_true,y_pred,from_logits=False)
    neg_loss = negitive_mask * K.pow(K.stop_gradient(y_pred), 2) * K.binary_crossentropy(y_true,y_pred,from_logits=False)
    loss = pos_loss + neg_loss
    return loss


class EdgeDetection(object):
    def __init__(self, model_path):
        self.model = load_model(model_path, custom_objects={'tf': tf, 'model_loss': model_loss})

    def detect_image(self, image, threshold=0.2):
        image_vec_01 = np.mean(image, axis=0)
        image_vec_02 = np.std(image, axis=0)
        image_vec_03 = np.zeros_like(image_vec_01)
        image_vec_03[:-1] = image_vec_01[1:] - image_vec_01[:-1]

        image_vec_01 = np.expand_dims(image_vec_01, axis=1)
        image_vec_01 = np.expand_dims(image_vec_01, axis=0)
        image_vec_02 = np.expand_dims(image_vec_02, axis=1)
        image_vec_02 = np.expand_dims(image_vec_02, axis=0)
        image_vec_03 = np.expand_dims(image_vec_03, axis=1)
        image_vec_03 = np.expand_dims(image_vec_03, axis=0)
        image_vec = np.concatenate([image_vec_01, image_vec_02, image_vec_03], axis=-1)

        result = self.model.predict(image_vec)
        result = np.squeeze(result)
        result = np.where(result > threshold)

        if len(result) == 0:
            return None
        else:
            result = result[0]
            filter_ = set([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 1020, 1021, 1022, 1023])
            result = set(result.tolist())
            result = list(result - filter_)
            if len(result) == 0:
                return None

            x_min = np.min(result)
            x_max = np.max(result)
            return x_min, x_max



# im_path = r'E:\EdgeDetection\dataset_01\4_69.jpg'
# image = Image.open(im_path)
# image = np.array(image)
# result = model.detect_image(image)
# pritn(result)

model_path = r'C:\Windows\System32\m.h5'

sess = tf.Session()
graph = tf.get_default_graph()

# 在model加载前添加set_session
set_session(sess)
model = EdgeDetection(model_path)
@CNT
@TicToc
def get_border(image):
    global sess
    global graph
    set_session(sess)
    with graph.as_default():
        result = model.detect_image(image/255.0)
        return result


if __name__ == "__main__":
    img_path = r"E:\4_40.jpg"
    I = cv2.imread(img_path,0).astype(np.uint8)

    import time
    for i in range(20):
        tic = time.time()
        print(get_border(I))
        print(time.time()-tic)