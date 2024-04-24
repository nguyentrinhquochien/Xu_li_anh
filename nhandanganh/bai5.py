import argparse
import numpy as np
import imutils
from scipy.spatial import distance as dist
from collections import OrderedDict
import cv2

count = 0

class ShapeDetector:
	def __init__(self):
		pass
	def detect(self, c):
		# initialize the shape name and approximate the contour
		shape = "unidentified"
		peri = cv2.arcLength(c, True)
		approx = cv2.approxPolyDP(c, 0.04 * peri, True)
        # if the shape is a triangle, it will have 3 vertices
		if len(approx) == 3:
			shape = "Triangle"
		# if the shape has 4 vertices, it is either a square or
		# a rectangle
		elif len(approx) == 4:
			# compute the bounding box of the contour and use the
			# bounding box to compute the aspect ratio
			(x, y, w, h) = cv2.boundingRect(approx)
			ar = w / float(h)
			# a square will have an aspect ratio that is approximately
			# equal to one, otherwise, the shape is a rectangle
			shape = "Square" if ar >= 0.95 and ar <= 1.05 else "Rectangle"
		# if the shape is a pentagon, it will have 5 vertices
		elif len(approx) == 5:
			shape = "Pentagon"
		# otherwise, we assume the shape is a circle
		else:
			shape = "Circle"
		# return the name of the shape
		return shape

class ColorLabeler:
	def __init__(self):
		# initialize the colors dictionary, containing the color
		# name as the key and the RGB tuple as the value
		colors = OrderedDict({
			"Red": (255, 0, 0),
			"Green": (0, 255, 0),
			"Blue": (0, 0, 255),
			"Orange": (255,165,0),
			"Yellow": (255,255,0)},
        )
		# allocate memory for the L*a*b* image, then initialize
		# the color names list
		self.lab = np.zeros((len(colors), 1, 3), dtype="uint8")
		self.colorNames = []
		# loop over the colors dictionary
		for (i, (name, rgb)) in enumerate(colors.items()):
			# update the L*a*b* array and the color names list
			self.lab[i] = rgb
			self.colorNames.append(name)
		# convert the L*a*b* array from the RGB color space
		# to L*a*b*
		self.lab = cv2.cvtColor(self.lab, cv2.COLOR_RGB2LAB)
  
	def label(self, image, c):
	# construct a mask for the contour, then compute the
	# average L*a*b* value for the masked region
		mask = np.zeros(image.shape[:2], dtype="uint8")
		cv2.drawContours(mask, [c], -1, 255, -1)
		mask = cv2.erode(mask, None, iterations=2)
		mean = cv2.mean(image, mask=mask)[:3]
		# initialize the minimum distance found thus far
		minDist = (np.inf, None)
		# loop over the known L*a*b* color values
		for (i, row) in enumerate(self.lab):
			# compute the distance between the current L*a*b*
			# color value and the mean of the image
			d = dist.euclidean(row[0], mean)
			# if the distance is smaller than the current distance,
			# then update the bookkeeping variable
			if d < minDist[0]:
				minDist = (d, i)
		# return the name of the color with the smallest distance
		return self.colorNames[minDist[1]]

image = cv2.imread(cv2.samples.findFile("./shape.jpg"))
# resized = imutils.resize(image, width=300)
ratio = image.shape[0] / image.shape[0]

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(image, (5, 5), 0)
lab = cv2.cvtColor(blurred, cv2.COLOR_BGR2LAB)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]

cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
sd = ShapeDetector()
cl = ColorLabeler()

# loop over the contours
for index, c in enumerate(cnts):
    # compute the center of the contour
    if(index != 0):
        M = cv2.moments(c)
        count += 1
        # print(M)  
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        # draw the contour and center of the shape on the image
        shape = sd.detect(c)
        color = cl.label(lab, c)
        # multiply the contour (x, y)-coordinates by the resize ratio,
        # then draw the contours and the name of the shape on the image
        c = c.astype("float")
        c *= ratio
        c = c.astype("int")
        text = "{} {}".format(color, shape)

        cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
        cv2.circle(image, (cX, cY), 7, (255, 255, 255), -1)
        cv2.putText(image, "center", (cX - 20, cY - 30),
        	cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(image, text , (cX + 10, cY + 10), cv2.FONT_HERSHEY_SIMPLEX,
		0.4, (204, 0, 102), 1)
        # cv2.putText(image, shape, (cX - 60, cY - 20), cv2.FONT_HERSHEY_SIMPLEX,
		# 0.4, (204, 0, 102), 1)
        # show the image

cv2.putText(image, "Number for shape: " + str(count), (30, 30),
    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
cv2.imshow("Image", image)
cv2.waitKey(0)