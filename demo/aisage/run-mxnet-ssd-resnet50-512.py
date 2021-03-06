#!/usr/bin/env python3

import os
import dlr
import numpy as np
import time

ms = lambda: int(round(time.time() * 1000))

test_image = "dog.jpg"
dshape = (1, 3, 512, 512)
dtype = "float32"

# Preprocess image
def open_and_norm_image(f):
    import cv2
    orig_img = cv2.imread(f)
    img = cv2.resize(orig_img, (dshape[2], dshape[3]))
    img = img[:, :, (2, 1, 0)].astype(np.float32)
    img -= np.array([123, 117, 104])
    img = np.transpose(np.array(img), (2, 0, 1))
    img = np.expand_dims(img, axis=0)
    return orig_img, img

model_path = "models/mxnet-ssd-resnet50-512"
print(model_path)

class_names = ["aeroplane", "bicycle", "bird", "boat", "bottle", "bus", "car", "cat", "chair",
               "cow", "diningtable", "dog", "horse", "motorbike", "person", "pottedplant",
               "sheep", "sofa", "train", "tvmonitor"]

######################################################################
# Load the model
device = 'opencl'
m = dlr.DLRModel(model_path, device)

orig_img, img_data = open_and_norm_image(test_image)
input_data = img_data.astype(dtype)

# dryrun
print("Warming up...")
m.run(input_data)
# execute
print("Running...")
N = 10
for i in range(N):
    t1 = ms()
    m_out = m.run(input_data)
    # get outputs
    out = m_out[0][0]
    t2 = ms()
    print("time: {} ms".format(t2 - t1))

i = 0
for det in out:
    cid = int(det[0])
    if cid < 0:
        continue
    score = det[1]
    if score < 0.5:
         continue
    i += 1

    print(i, class_names[cid], det)

######################################################################
# Display result

def display(img, out, thresh=0.5):
    import random
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    mpl.rcParams['figure.figsize'] = (10, 10)
    pens = dict()
    plt.clf()
    plt.imshow(img)
    for det in out:
        cid = int(det[0])
        if cid < 0:
            continue
        score = det[1]
        if score < thresh:
            continue
        if cid not in pens:
            pens[cid] = (random.random(), random.random(), random.random())
        scales = [img.shape[1], img.shape[0]] * 2
        xmin, ymin, xmax, ymax = [int(p * s) for p, s in zip(det[2:6].tolist(), scales)]
        rect = plt.Rectangle((xmin, ymin), xmax - xmin, ymax - ymin, fill=False,
                             edgecolor=pens[cid], linewidth=3)
        plt.gca().add_patch(rect)
        text = class_names[cid]
        plt.gca().text(xmin, ymin-2, '{:s} {:.3f}'.format(text, score),
                       bbox=dict(facecolor=pens[cid], alpha=0.5),
                       fontsize=12, color='white')
    plt.show()

#image = cv2.cvtColor(orig_img, cv2.COLOR_BGR2RGB)
#display(image, out, thresh=0.5)
