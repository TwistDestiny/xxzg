import numpy as np

import cv2
def make_water_mark(image_path):
    image = cv2.imread(image_path)
    # 转换为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 像素翻转
    thresh = cv2.threshold(gray, 225, 255, cv2.THRESH_BINARY_INV)[1]
    cv2.imwrite(image_path, thresh)

    image = cv2.imread(image_path)

    (h, w) = image.shape[:2]
    image = np.dstack([image, np.ones((h, w), dtype="uint8") * 255])
    print(image.shape)
    cv2.imwrite(image_path, image)
def load_water_mark(image_path):
    watermark = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if watermark is None:
        raise Exception("{}水印文件不存在".format(image_path))
    (wH, wW) = watermark.shape[:2]
    (B, G, R, A) = cv2.split(watermark)
    B = cv2.bitwise_and(B, B, mask=A)
    G = cv2.bitwise_and(G, G, mask=A)
    R = cv2.bitwise_and(R, R, mask=A)
    watermark = cv2.merge([B, G, R, A])

    return watermark



def add_watermark(image,watermark,alpha=0.01):
    (h, w) = image.shape[:2]
    (wH, wW) = watermark.shape[:2]
    image = np.dstack([image, np.ones((h, w), dtype="uint8") * 255])

    # 构建水印图片的叠加层（使得其具有与输入图像完全相同的宽度和高度）
    if h != wW and w!=wH:
        watermark = cv2.resize(watermark,(w,h))
    # 应用cv2.addWeighted构造水印的图像
    output = image.copy()
    cv2.addWeighted(watermark, alpha, output, 1.0, 0, output)
    return output

def make():
    make_water_mark(r"C:\Users\wang_\Pictures\tmp\logo1.png")

def main():


    img_path = r"C:\Users\wang_\Pictures\4_247.jpg"
    # 使用photoshop（纯白底 纯黑字创建图像），导出不带透明度的logo
    watermark_path = r"C:\Users\wang_\Pictures\tmp\logo.png"
    # make_water_mark(watermark_path)

    o = add_watermark(cv2.imread(img_path),load_water_mark(watermark_path),0.1)

    # 展示
    import matplotlib.pyplot as plt
    o = o[:, :, [2, 1, 0]]
    plt.imshow(o)
    plt.show()
if __name__ == "__main__":
    main()
    pass

