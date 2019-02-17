#run this to make sure you're cv2 is working

import numpy as np
import cv2
img = cv2.imread('hope.png')
cv2.imshow('My photo', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
