import cv2
import numpy as np

def de(img,kernel):
	eroded=cv2.erode(img,kernel);
	dilated = cv2.dilate(img,kernel)
	result = cv2.absdiff(dilated,eroded);
	return result

def find_edge(img,thresh):
	# get gray img
	gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	# threshold with thresh
	ret, thresh_w = cv2.threshold(gray,thresh,255,cv2.THRESH_BINARY)
	img_h = img.shape[0]
	img_w = img.shape[1]
	res = np.zeros((img_h,img_w))
	flags = [0]*img_h
	for row in range(0,img_h):
		for col in range(0,img_w):
			if thresh_w[row,col] == 255:
				res[row,col] = 255
				flags[row] = 1
				break
			else:
				pass
	for row in range(-1,-img_h,-1):
		for col in range(-1,-img_w,-1):
			if thresh_w[row,col] == 255:
				res[row,col] = 255
				break
			else:
				pass
	return res[0:flags.index(0),:], flags.index(0)

w_img = cv2.imread("./imgs/wrong_type_1.bmp")
r_img = cv2.imread("./imgs/right.bmp")
illumination_mask = cv2.imread("./imgs/mask.png")
kernel = np.ones((5,5),np.uint8)

w_gray = cv2.cvtColor(w_img,cv2.COLOR_BGR2GRAY)
r_gray = cv2.cvtColor(r_img,cv2.COLOR_BGR2GRAY)
ret, thresh_w = cv2.threshold(w_gray,50,255,cv2.THRESH_BINARY_INV)
ret, thresh_r = cv2.threshold(r_gray,50,255,cv2.THRESH_BINARY_INV)

# cv2.imshow('thresh_w',thresh_w)
# cv2.imshow('thresh_r',thresh_r)
# cv2.imshow('w_gray',w_gray)
# cv2.imshow('r_gray',r_gray)
cv2.waitKey(0)
cv2.destroyAllWindows()

w_gradient = de(w_img,kernel)
r_gradient = de(r_img,kernel)
w_edge, w_end = find_edge(w_gradient,30)
r_edge, r_end = find_edge(r_gradient,30)

# print(w_end)
# print(r_end)
point4_wsum = sum(sum(thresh_w[w_end-155:w_end-115,:]))
point4_rsum = sum(sum(thresh_r[r_end-155:r_end-115,:]))
print(point4_rsum)
print(point4_wsum)
cv2.imshow("w_edge",thresh_w[w_end-155:w_end-115,:])
cv2.imshow("r_edge",thresh_r[r_end-155:r_end-115,:])
cv2.waitKey(0)
cv2.destroyAllWindows()