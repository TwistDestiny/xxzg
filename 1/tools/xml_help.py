from functools import reduce
import glob
import tqdm
import os
from io import StringIO
from PIL import Image
import numpy as np
import xml.etree.ElementTree as ET
from collections import defaultdict

def compose(*funcs):
    """Compose arbitrarily many functions, evaluated left to right.

    Reference: https://mathieularose.com/function-composition-in-python/
    """
    # return lambda x: reduce(lambda v, f: f(v), funcs, x)
    if funcs:
        return reduce(lambda f, g: lambda *a, **kw: g(f(*a, **kw)), funcs)
    else:
        raise ValueError('Composition of empty sequence not supported.')

def get_classes(file_path):
    with open(file_path) as f:
        classes = [line.strip() for line in f.readlines()]
    return classes

def get_anchors(file_path):
    with open(file_path) as f:
        anchors = f.readline()
    anchors = [float(x) for x in anchors.split(',')]
    return np.array(anchors).reshape(-1, 2)

def get_dataset(file_path):
    with open(file_path) as f:
        lines = [line.strip() for line in f.readlines()]
    return lines

def parse_xml(file, classes=None):
    tree = ET.parse(file)
    root = tree.getroot()
    objects = root.findall('object')
    boxes = []
    for obj in objects:
        name = obj.findtext('name')
        box = [int(obj.find('bndbox').findtext(key)) for key in ['xmin', 'ymin', 'xmax', 'ymax']]
        if classes:
            name = classes.index(name)
        box.append(name)
        boxes.append(box)

    im_fp = None
    if os.path.exists(os.path.abspath(os.path.splitext(file)[0]+'.jpg')):
        im_fp  = os.path.abspath(os.path.splitext(file)[0]+'.jpg')
    elif os.path.exists(os.path.abspath(os.path.splitext(file)[0]+'.bmp')):
        im_fp = os.path.abspath(os.path.splitext(file)[0]+'.bmp')
    return im_fp, boxes

def parse_line(annotation_line, loadImage=True, box_type='np', image_type='np'):

    line = annotation_line.split()
    im_fp = line[0]
    image = None
    if loadImage:
        image = Image.open(im_fp).convert('RGB')
        if image_type == 'Image':
            pass
        elif image_type == 'np':
            image = np.array(image)
        else:
            pass

    boxes =[box.split(',') for box in line[1:]]
    if box_type == 'list':
        pass
    elif box_type == 'np':
        boxes = np.array(boxes)
    else:
        pass

    return im_fp, boxes, image


def get_dataset_list(data_dirs, shuffle = False):
    files = []
    for i, dir in enumerate(data_dirs):
        xml_files = glob.glob(os.path.join(dir, "*.xml"))
        xml_files = [xml_file for xml_file in xml_files if
                     os.path.exists(os.path.join(dir, os.path.splitext(xml_file)[0] + '.jpg')) or os.path.exists(os.path.join(dir, os.path.splitext(xml_file)[0] + '.bmp'))]
        files.extend(xml_files)

    f = StringIO()
    for xml_file in tqdm.tqdm(files):
        im_fp, boxes = parse_xml(xml_file)
        f.write(im_fp)
        for box in boxes:
            f.write(" " + ",".join(list(map(str, box))))
        f.write('\n')

    lines = f.getvalue()
    lines = lines.split('\n')
    lines = [line.strip() for line in lines if line != '']

    if shuffle:
        np.random.seed(10101)
        np.random.shuffle(lines)
        np.random.seed(None)
    return lines

def rand(a=0, b=1):
    return np.random.rand() * (b - a) + a


def filter_image(image, boxes, classes, box_type='np', image_type='np'):

    if not isinstance(image, np.ndarray):
        image = np.array(image)

    valid_boxes = []
    for box in boxes:
        x1,y1,x2,y2,c = box
        x1,y1,x2,y2 = list(map(int,[x1,y1,x2,y2]))
        if not (c in classes):
            image[y1:y2,x1:x2,:] = 0
        else:
            valid_boxes.append([x1,y1,x2,y2,classes.index(c)])

    if image_type == 'Image':
        image = Image.fromarray(image)
    elif image_type == 'np':
        pass
    else:
        pass

    if box_type == 'list':
        pass
    elif box_type == 'np':
        valid_boxes = np.array(valid_boxes)
    else:
        pass
    return image, valid_boxes


def clip_image_boxes(image, boxes, thres = 0.6, box_type = 'np', image_type='np'):

    if not isinstance(image,np.ndarray):
        image = np.array(image)

    if not isinstance(boxes,np.ndarray):
        boxes = np.array(boxes)


    h, w = image.shape[0], image.shape[1]

    boxes_w = boxes[:, 2] - boxes[:, 0]
    boxes_h = boxes[:, 3] - boxes[:, 1]

    boxes = boxes[(boxes_w * boxes_h)>0]
    boxes_w = boxes[:, 2] - boxes[:, 0]
    boxes_h = boxes[:, 3] - boxes[:, 1]

    boxes[:, 0] = np.minimum(np.maximum(boxes[:, 0], 1), w - 1)
    boxes[:, 1] = np.minimum(np.maximum(boxes[:, 1], 1), h - 1)
    boxes[:, 2] = np.minimum(np.maximum(boxes[:, 2], 1), w - 1)
    boxes[:, 3] = np.minimum(np.maximum(boxes[:, 3], 1), h - 1)
    boxes_wclip = boxes[:, 2] - boxes[:, 0]
    boxes_hclip = boxes[:, 3] - boxes[:, 1]


    ratios = (boxes_wclip * boxes_hclip) / (boxes_w * boxes_h)
    for i, ratio in enumerate(ratios):
        if ratio < thres:
            box = boxes[i]
            x1, y1, x2, y2, c = box
            image[y1:y2, x1:x2, :] = 125
    boxes = boxes[ratios > thres]


    if image_type == 'Image':
        image = Image.fromarray(image)
    elif image_type == 'np':
        pass
    else:
        pass

    if box_type == 'list':
        boxes = boxes.tolist()
    elif box_type == 'np':
        pass
    else:
        pass

    return image, boxes





def calculate_theta(boxes):

    if len(boxes) <2:
        return None

    center_x = (boxes[... ,0 ] +boxes[... ,2] ) /2.0
    center_y = (boxes[... ,1 ] +boxes[... ,3] ) /2.0
    center = np.stack([center_x ,center_y] ,axis=1)

    point1 = np.expand_dims(center.copy() ,axis=1)
    point2 = np.expand_dims(center.copy() ,axis=0)

    delta = point1 - point2
    delta_x = np.triu(delta[... ,0])
    delta_y = np.triu(delta[... ,1])

    delta_y = delta_y[delta_x!=0]
    delta_x = delta_x[delta_x!=0]
    k = delta_y /delta_x


    if len(k)>0:
        rads = np.arctan(k)
        rads[rads <0] = rads[rads <0 ] +np.pi
        degs = np.rad2deg(rads)

        degs_map = defaultdict(list)
        for deg in degs:
            if len(degs_map.keys()) == 0:
                degs_map[deg].append(deg)
            else:
                adding = False
                for key in degs_map:
                    if abs(key -deg ) <10:
                        degs_map[key].append(deg)
                        adding = True
                if not adding:
                    degs_map[deg].append(deg)

        target_deg = list(degs_map.keys())[0]
        for key in degs_map:
            if len(degs_map[key]) > len(degs_map[target_deg]):
                target_deg = key

        target_deg = np.mean(degs_map[target_deg])


        return target_deg
    else:
        return None


import xml.etree.ElementTree as ET


def create_xml_file(output_dir, xml_name, boxes, classes=None):
    root = ET.Element('annotation')
    filename = ET.SubElement(root, 'filename')
    filename.text = xml_name.split('.')[0] + '.jpg'

    if boxes is None:
        boxes = []
    boxes = np.array(boxes, dtype='int32')

    for box in boxes:
        if len(box) == 5:
            x1, y1, x2, y2, c = box

        if len(box) == 6:
            x1, y1, x2, y2, c, _ = box

        if classes:
            c = classes[c]

        object = ET.SubElement(root, 'object')
        name = ET.SubElement(object, 'name')
        name.text = c

        bndbox = ET.SubElement(object, 'bndbox')
        xmin = ET.SubElement(bndbox, 'xmin')
        xmin.text = str(x1)
        ymin = ET.SubElement(bndbox, 'ymin')
        ymin.text = str(y1)
        xmax = ET.SubElement(bndbox, 'xmax')
        xmax.text = str(x2)
        ymax = ET.SubElement(bndbox, 'ymax')
        ymax.text = str(y2)
    tree = ET.ElementTree(root)
    tree.write(os.path.join(output_dir, xml_name))


def v_iou_box(box_, boxes2_):
    box = np.expand_dims(box_, 0)
    boxes2 = boxes2_
    top = np.maximum(box[..., 1], boxes2[..., 1])
    bottom = np.minimum(box[..., 3], boxes2[..., 3])
    intersect = np.maximum(bottom - top, 0)
    iou = intersect / (box[..., 3] - box[..., 1])
    return iou

def sort_boxes(boxes):
    if boxes is not None and len(boxes) > 0:
        if not isinstance(boxes, np.ndarray):
            boxes = np.array(boxes)

        assert len(boxes.shape) == 2, 'boxes shape should be two dimension'

        tag = np.zeros(len(boxes))
        tag = np.expand_dims(tag, axis=1)
        boxes = np.concatenate((boxes, tag), axis=1)

        lines = []
        line = []
        lines.append(line)

        boxes = boxes[np.argsort(boxes[..., 0])]
        best_idx = 0
        head = boxes[best_idx]
        head[-1] = 1
        line.append(head.tolist())

        while np.any(boxes[..., -1] == 0):

            overlaps = v_iou_box(head, boxes)
            find = False
            for i in range(best_idx, len(boxes)):
                box = boxes[i]
                overlap = overlaps[i]
                if box[-1] != 1 and overlap > 0.25 and (box[0] >head[0])>0:
                    head = box
                    head[-1] = 1
                    line.append(head)
                    best_idx = i
                    find = True
                    break

            if not find:
                line = []
                lines.append(line)
                for i in range(len(boxes)):
                    box = boxes[i]
                    if box[-1] != 1:
                        best_idx = i
                        head = box
                        head[-1] = 1
                        line.append(head)
                        break

        lines = [np.array(line) for line in lines]
        mean_line_y = [np.mean(line[..., 1]) for line in lines]
        indices = np.argsort(mean_line_y).tolist()

        sorted_line = []
        for idx in indices:
            sorted_line.append(lines[idx])

        return sorted_line
    else:
        return []