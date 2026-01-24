import numpy as np
import cv2

canvas = np.zeros((300, 300, 3), dtype = np.uint8)

canvas[0:100, 0:100] = [0, 0, 255]

center_piece = canvas[100:200, 100:200].copy()

center_piece[:] = [0, 255, 0]

red_channel = canvas[:, :, 2]

cv2.imshow('Canvas', canvas)
cv2.imshow('Red Channel', red_channel)


cv2.waitKey(0)
cv2.destroyAllWindows()