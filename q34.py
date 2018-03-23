import cv2
import numpy as np
import math

def de(img,kernel):
	eroded=cv2.erode(img,kernel);
	dilated = cv2.dilate(img,kernel)
	result = cv2.absdiff(dilated,eroded);
	return result

def find_edge(img,thresh):
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

def detect_blue(input_img,hsv):
	img_h = input_img.shape[0]
	img_w = input_img.shape[1]
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
	upper_bound = 0;
	for l in lines:
		if l > 100:
			# print(lines.index(l))
			upper_bound = lines.index(l)
			break
	return res,upper_bound,lines

def feature_imgs(img,thresh,output_width,output_height):
	kernel = np.ones((5,5),np.uint8)
	gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	ret, binary = cv2.threshold(gray,thresh,255,cv2.THRESH_BINARY_INV)
	gradient = de(img,kernel)
	edges, lower_bound, left_bound, right_bound = find_edge(gradient,thresh)
	blue_area, upper_bound, blue_lines  = detect_blue(img,hsv)

	edges = cv2.resize(edges[upper_bound:lower_bound,left_bound:right_bound],(output_width,output_height),interpolation=cv2.INTER_CUBIC)
	gray = cv2.resize(gray[upper_bound:lower_bound,left_bound:right_bound],(output_width,output_height),interpolation=cv2.INTER_CUBIC)
	blue_area = cv2.resize(blue_area[upper_bound:lower_bound,left_bound:right_bound],(output_width,output_height),interpolation=cv2.INTER_CUBIC)
	gradient = cv2.resize(gradient[upper_bound:lower_bound,left_bound:right_bound],(output_width,output_height),interpolation=cv2.INTER_CUBIC)
	binary = cv2.resize(binary[upper_bound:lower_bound,left_bound:right_bound],(output_width,output_height),interpolation=cv2.INTER_CUBIC)
	img = cv2.resize(img[upper_bound:lower_bound,left_bound:right_bound],(output_width,output_height),interpolation=cv2.INTER_CUBIC)
	hsv = cv2.resize(hsv[upper_bound:lower_bound,left_bound:right_bound],(output_width,output_height),interpolation=cv2.INTER_CUBIC)
	return gray, hsv, binary, gradient, edges, blue_area, img, upper_bound, lower_bound, left_bound, right_bound, blue_lines

def point4(binary,upper,lower,threshold):
	mount = sum(sum(binary[upper:lower,:]))/255
	print(mount)
	if mount < threshold:
		flags[3] = 0

def point3(binary,upper,lower,threshold):
	mount = sum(sum(binary[upper:lower,:]))/255
	print('point3 ',mount)
	if mount < threshold:
		flags[2] = 0

def point2(edges,upper,lower,threshold):
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
	if right-left > threshold:
		flags[1] = 0
	# print('left ', left, ' right ',right, ' right-left ',right-left)
	# cv2.imshow('ed',edges[upper:lower,cc:img_w])
	# print('rows ', rows)
def point1(blue_lines,upper,lower,upper_bound,lower_bound):
	blue_lines = blue_lines[upper_bound:lower_bound]
	part = math.floor((lower-upper)/3)
	upper_part = max(blue_lines[upper:upper+part])
	lower_part = max(blue_lines[lower-2*part:lower])
	max_part = max(blue_lines[upper:lower])
	if upper_part == max_part  :
		flags[0] = 0
	print(' upper_part ', upper_part)
	print(' lower_part ', lower_part)
	print('max ',max_part)

w_img = cv2.imread("./imgs/wrong_type_1.bmp")
# r_img = cv2.imread("./imgs/bigr.bmp")
img_h = 430
img_w = 320
flags = [1,1,1,1]

################################################################################
# threshold from 30 to 50 is recomended
gray, hsv, binary, gradient, edges, blue_area, img, upper_bound, lower_bound, left_bound, right_bound, blue_lines = feature_imgs(w_img,30,img_w,img_h)
print('upper ',upper_bound,' lower ',lower_bound, ' left ',left_bound,' right ',right_bound)

# p4[270:300]
# p3[255:265]
# p2[50:80]
# p1[0:50]
point1(blue_lines,0,50,upper_bound,lower_bound)
# recomended threshold = 25
point2(edges,50,80,25)
# recomended threshold = 20
point3(binary,255,265,30)
# recomended threshold = 60
point4(binary,270,300,60)

################################################################################
# imshow
cv2.imshow('gray',gray)
cv2.imshow('blue_area',blue_area[0:32])
cv2.imshow('binary',binary)
cv2.imshow('binary_p3',binary[255:265])
cv2.imshow('edges',edges[50:80])
cv2.imshow('gradient',gradient)
cv2.waitKey(0)
cv2.destroyAllWindows()
print(flags)
