import numpy as np
import matplotlib.pyplot as plt
import cv2
import os
import imutils

folder = "../renders/ImagingSession1_27keV"

# loop through all images in folder
for image in os.listdir(folder):
    # load image
    img = cv2.imread(folder + "/" + image, 0)
    # convert to float and normalize
    img = img.astype(np.float32)
    img /= 255
    # invert image
    img = 1 - img
    # convert image to color
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    # get mean pixel value and std dev of square
    square = img[int(img.shape[0]/2 - 50):int(img.shape[0]/2 + 50), int(img.shape[1]/2 - 50):int(img.shape[1]/2 + 50)]
    mean, std = cv2.meanStdDev(square)
    print("Image: " + image + " Mean: " + str(mean[0][0]) + " Std Dev: " + str(std[0][0]))
    # unnormalize image, convert to uint8
    img *= 255
    img = img.astype(np.uint8)
    # draw red square at center of image
    cv2.rectangle(img, (int(img.shape[1] / 2 - 50), int(img.shape[0] / 2 - 50)),
                  (int(img.shape[1] / 2 + 50), int(img.shape[0] / 2 + 50)), (0, 0, 255), 2)


    cv2.imwrite(folder + "_processed/" + image, img)


