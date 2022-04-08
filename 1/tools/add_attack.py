import cv2
import numpy as np
def lapalian_demo(image): #拉普拉斯算子
    dst = cv2.Laplacian(image, cv2.CV_32F)
    lpls = cv2.convertScaleAbs(dst)
    return lpls
def attack(image, epsilon):
    """
    获取扰动图片
    :param image: 原始图片
    :param epsilon: 扰动量
    :param data_grad: 损失梯度
    :return:
    """
    # Collect the element-wise sign of the data gradient
    sign_data_grad = lapalian_demo(image)

    # Create the perturbed image by adjusting each pixel of the input image
    perturbed_image = image + epsilon*sign_data_grad

    return perturbed_image.astype(np.uint8)


if __name__ == "__main__":
    img_path = r"C:\Users\wang_\Pictures\4_247.jpg"
    o = attack(cv2.imread(img_path),0.5)

    # o =lapalian_demo(cv2.imread(img_path))
    # o = o*0.5
    # o = o.astype(np.uint8)

    import matplotlib.pyplot as plt
    o = o[:, :, [2, 1, 0]]
    plt.imshow(o)
    plt.show()