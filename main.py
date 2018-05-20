import cv2
import numpy as np
import math

# find gradient
def de(img,kernel):
	eroded=cv2.erode(img,kernel);
	dilated = cv2.dilate(img,kernel)
	result = cv2.absdiff(dilated,eroded);
	return result

# contour the edge of component
def findEdge(img,thresh):
	# get gray img
	gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	# threshold with thresh
	ret, binary = cv2.threshold(gray,thresh,255,cv2.THRESH_BINARY)
	img_h = img.shape[0]
	img_w = img.shape[1]
	res = np.zeros((img_h,img_w))
	flags_row = [0]*img_h
	flags_col = [0]*img_w
	for row in range(0,img_h):
		for col in range(0,img_w):
			if binary[row,col] == 255:
				res[row,col] = 255
				flags_row[row] = 1
				flags_col[col] = 1
				break
			else:
				pass
	for row in range(-1,-img_h,-1):
		for col in range(-1,-img_w,-1):
			if binary[row,col] == 255:
				res[row,col] = 255
				flags_col[col] = 1
				break
			else:
				pass
	for x in range(img_w-1,0,-1):
		if flags_col[x] == 1:
			right_end = x
			break
	return res, flags_row.index(0), flags_col.index(1), right_end

# detect blue area
def detectBlue(input_img,hsv):
	img_h = input_img.shape[0]
	img_w = input_img.shape[1]
	flag = 0
	# hsv = cv2.cvtColor(input_img, cv2.COLOR_BGR2HSV)
	H, S, V = cv2.split(hsv)
	lower_blue=np.array([80,43,46])
	upper_blue=np.array([130,255,255])
	mask = cv2.inRange(hsv, lower_blue, upper_blue)
	#cv2.imshow('Mask', mask)
	res = cv2.bitwise_and(hsv,hsv, mask=mask)
	left_edge_list = np.zeros(img_h,dtype=np.int)
	right_edge_list = np.zeros(img_h,dtype=np.int)
	lines=[0]*img_h
	for x in range(0,img_h):
		target_point = 0
		left_trigger = 0
		right_trigger = 0
		for y0 in res[x]:
			if y0[0]!=0:
				target_point+=1
		lines[x] = target_point
	# print(lines)
	# print('line_max= ', max(lines))
	lineThresh = max(lines) - 30
	upper_bound = 0
	for l in range(img_h):
		if lines[l] > lineThresh and flag == 0:
			upper_bound = l
			flag += 1
		if lines[l] < lineThresh and lines[l+1] < lineThresh and flag == 1:
			lower_bound = l
			break
	return res,upper_bound,lines,lower_bound

def featureImg(img,thresh):
	kernel = np.ones((5,5),np.uint8)
	gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	ret, binary = cv2.threshold(gray,thresh,255,cv2.THRESH_BINARY_INV)
	gradient = de(img,kernel)
	edges, lower_bound, left_bound, right_bound = findEdge(gradient,thresh)
	blue_area, upper_bound, blue_lines, blue_lower_bound  = detectBlue(img,hsv)

	edges = edges[upper_bound:lower_bound,left_bound:right_bound]
	gray = gray[upper_bound:lower_bound,left_bound:right_bound]
	blue_area = blue_area[upper_bound:lower_bound,left_bound:right_bound]
	gradient = gradient[upper_bound:lower_bound,left_bound:right_bound]
	binary = binary[upper_bound:lower_bound,left_bound:right_bound]
	img = img[upper_bound:lower_bound,left_bound:right_bound]
	hsv = hsv[upper_bound:lower_bound,left_bound:right_bound]
	return hsv, binary, gradient, edges, blue_area, img, upper_bound, lower_bound, left_bound, right_bound, blue_lines, blue_lower_bound

def point3(binary,upper,lower,threshold):
	whitep = sum(sum(binary[upper:lower,:]))/255
	width = np.size(binary,1)
	totalPixels = (lower-upper)*width
	# print('height ',lower-upper)
	# print('width ',width)
	# average = np.average(np.average(binary[upper:lower,:]))
	# print((lower-upper)*width)
	# print('average ',mount/(lower-upper)/width)
	# print('mount ',mount)
	print('p3 mount/totalPixels = ',whitep/totalPixels)
	if whitep/totalPixels < 0.01:
		flags[3] = 0


def point2(edges,left,right,upper,lower,threshold):
	img_h = lower - upper
	img_w = right - left
	columns = [0]*img_w
	rows = [0]*img_h
	for r in range(0,img_h):
		for c in range(0,img_w):
			edges[r,c] = max(0,edges[r,c])
			if edges[r,c] > 0:
				edges[r,c] = 255;
	for col in range(math.floor(img_w/2),img_w):
		if sum(edges[upper:lower,col]) > 0:
			columns[col] = 1
	left = columns.index(1)
	for cc in range(img_w-1,0,-1):
		if columns[cc] == 1:
			right = cc
			break
	print(right-left)
	if right-left > threshold:
		flags[1] = 0

def point1(blue_lines,upper_bound,lower_bound):
	half = math.floor((lower_bound - upper_bound)/2)
	upper_part = max(blue_lines[upper_bound:upper_bound+half])
	lower_part = max(blue_lines[lower_bound-half:lower_bound])
	max_part = max(blue_lines[upper_bound:blue_lower_bound])
	if upper_part == max_part  :
		flags[0] = 0
	print(' upper_part ', upper_part)
	print(' lower_part ', lower_part)
	print('max ',max_part)

def compSize(height,width):
	# a<c<b
	isMax = False
	ratio = height/width
	print('ratio ',ratio)
	if ratio > 1.5:
		isMax = True
	return isMax
	# if ratio < 1.268:
	#     print('this is the medium one')
	# elif ratio > 1.268 and ratio < 1.4:
	#     print('this is the minimum one')
	# elif ratio > 1.48 and ratio < 1.6:
	#     print('this is the maximum one')
	# else:
	#     print('Unknown type!!!');

################################################################################

img = cv2.imread("./imgs/111b.bmp")
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
img_h = np.size(gray,0)
img_w = np.size(gray,1)
flags = [1,1,1,1]

################################################################################
# threshold from 30 to 50 is recomended
hsv, binary, gradient, edges, blue_area, img, upper_bound, lower_bound, left_bound, right_bound, blue_lines, blue_lower_bound= featureImg(img,30)
print('upper ',upper_bound,' lower ',lower_bound, ' left ',left_bound,' right ',right_bound, ' blue_lower_bound ', blue_lower_bound)

# specify component type
isMax = compSize(np.size(edges,0),np.size(edges,1))
height = lower_bound - upper_bound
width = right_bound - left_bound
halfh = math.floor(height/2)
halfw = math.floor(width/2)

point1(blue_lines,upper_bound,blue_lower_bound)
# # recomended threshold = 15
point2(edges,left_bound,right_bound,blue_lower_bound-5-upper_bound,blue_lower_bound+10-upper_bound,15)

if isMax:
	p3upper = halfh-5
	p3lower = halfh+20
	point3(binary,p3upper,p3lower,10)
else:
	p3upper = math.floor(1.5*halfh)-20
	p3lower = math.floor(1.5*halfh)
	point3(binary,p3upper,p3lower,10)
# # recomended threshold = 20
# point3(binary,255,265,30)
# # recomended threshold = 60
# point4(binary,270,300,60)
# print(blue_lines)
################################################################################
# imshow
cv2.imshow('gray',gray)
cv2.imshow('p1',blue_area[0:blue_lower_bound-upper_bound,:])
cv2.imshow('blue_area',blue_area)
cv2.imshow('binary',binary)
cv2.imshow('p4',binary[p3upper:p3lower,:])
cv2.imshow('p2',edges[blue_lower_bound-10-upper_bound:blue_lower_bound+10-upper_bound,:])
cv2.imshow('edges',edges)
cv2.imshow('gradient',gradient)
cv2.waitKey(0)
cv2.destroyAllWindows()
print(flags)
