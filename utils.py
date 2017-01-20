import cv2
import numpy as np


def resize(image, width):
    # we need to keep in mind aspect ratio so the image does
    # not look skewed or distorted -- therefore, we calculate
    # the ratio of the new image to the old image
    r = float(width) / image.shape[1]
    dim = (width, int(image.shape[0] * r))
    return cv2.resize(image, dim, interpolation = cv2.INTER_AREA)


def show(image, title=''):
    cv2.imshow(title, image)
    cv2.waitKey(0)


# best one: cv2.COLOR_BGR2LAB
def color_sift(sift, image, color_model=cv2.COLOR_BGR2LAB):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    kps = sift.detect(gray, None)
    if len(kps) == 0:
        return [], np.array([])
    converted = image if color_model == None else cv2.cvtColor(image, color_model)
    _, d1 = sift.compute(converted[:, :, 0], kps)
    _, d2 = sift.compute(converted[:, :, 1], kps)
    _, d3 = sift.compute(converted[:, :, 2], kps)
    return kps, np.hstack([ d1, d2, d3 ])
