
import struct, json, math
import numpy as np
import cv2 as cv

import random

def get_bytes(buffer, length):
    bytes_ = buffer[:length]
    buffer = buffer[length:]
    return bytes_, buffer

def encode_unsign_long(num):
    return struct.pack('Q', num)

def parse_unsign_long(buffer):
    return struct.unpack('Q', buffer)[0]

def encode_data(data):
    num_to_send = len(data)
    num_to_send = struct.pack('Q',num_to_send)
    data_encoded = num_to_send
    for info_buffer, image_buffer in data:
        data_encoded = data_encoded + encode_unsign_long(len(info_buffer)) + info_buffer
        data_encoded = data_encoded + encode_unsign_long(len(image_buffer)) + image_buffer
    return data_encoded


def parse_encoded_data(data):
    num,data = get_bytes(data, 8)
    num = parse_unsign_long(num)
    result = []
    for i in range(num):
        info_buffer_length, data = get_bytes(data, 8)
        info_buffer_length = parse_unsign_long(info_buffer_length)
        info_buffer,data = get_bytes(data, info_buffer_length)
        info = json.loads(str(info_buffer, encoding='utf-8'))

        image_buffer_length,data = get_bytes(data, 8)
        image_buffer_length = parse_unsign_long(image_buffer_length)
        image_buffer,data = get_bytes(data, image_buffer_length)
        np_data  = np.frombuffer(image_buffer, dtype=np.uint8)
        np_data = np_data.reshape((np_data.shape[0], 1))
        image = cv.imdecode(np_data, cv.IMREAD_COLOR)[..., ::-1]
        result.append((info, image))
    return result


def split_data(buffer, buffer_size):
    buffer_arr = []
    buffer_size = buffer_size - 8 - 8 -8
    buffer_num = int(math.ceil(len(buffer)/buffer_size))
    uid = random.randint(0, 10000)
    for i in range(0,buffer_num):
        buffer_i, buffer = get_bytes(buffer, buffer_size)
        buffer_i = encode_unsign_long(uid) + encode_unsign_long(i) + encode_unsign_long(buffer_num) + buffer_i
        buffer_arr.append(buffer_i)
    return buffer_arr, uid

def combine_data(buffer_arr):
    buffer = b''
    for buffer_i in buffer_arr:
        buffer=buffer+buffer_i
    return buffer



def get_image_info(queue, num_to_send):
    data = []
    for i in range(num_to_send):
        try:
            (image, info) = queue.get(block=False)
            image_encode = cv.imencode('.jpg', image)[1]
            image_buffer = image_encode.tobytes()
            info['image_shape'] = image.shape
            info_buffer = bytes(json.dumps(info), encoding='utf-8')
        except Exception as e:
            pass
        else:
            data.append((info_buffer, image_buffer))
    return data
