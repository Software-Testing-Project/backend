# Decreasing the size of image
import cv2

x = cv2.imread("ehsan.jpg")
half = cv2.resize(x, (0, 0), fx=0.1, fy=0.1)
cv2.imwrite("ehsan1.jpg", half)
