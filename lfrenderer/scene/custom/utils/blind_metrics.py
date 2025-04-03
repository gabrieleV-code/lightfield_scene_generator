from math import log10, sqrt , ceil
import os
import cv2 
import numpy as np 
from os import listdir
import re
from os.path import isfile, join
import numpy as np
from skimage.metrics import structural_similarity as ssim
from brisque import BRISQUE

def load_images(mypath):
    onlyfiles = [ f for f in listdir(mypath) if isfile(join(mypath,f)) and re.search(r'\.png', f)] #and re.search(r'input_', f)
    images = np.empty(len(onlyfiles), dtype=object)
    for n in range(0, len(onlyfiles)):
        images[n] = cv2.imread( join(mypath,onlyfiles[n]) )
    return images

def PSNR(original, compressed): 
	mse = np.mean((original - compressed) ** 2) 
	if(mse == 0): # MSE is zero means no noise is present in the signal . 
				# Therefore PSNR have no importance. 
		return 100
	max_pixel = 255.0
	psnr = 20 * log10(max_pixel / sqrt(mse)) 
	return psnr 

def mean_PSNR(img_reference,img_set):
	psnr_mean = 0
	for img in img_set:
		psnr_img = PSNR(img_reference,img)
		psnr_mean = psnr_img + psnr_mean
	return 1/(len(img_set))*(psnr_mean)

def angular_PSNR(img_set):
    img_center = image_Center(img_set=img_set)
    psnr_mean = mean_PSNR(img_center,img_set)
    psnr_angular = 1/(img_center.shape[0]*img_center.shape[1]) * psnr_mean
    return psnr_angular

def aggregate_Mean_PSNR(img_set):
	psnr_mean_agg = 0
	psnr_mean=0
	for index_1,img_1 in enumerate(img_set):
		for index_2,img_2 in enumerate(img_set[index_1:]):
			if index_1==index_2:
				continue
			psnr_img = PSNR(img_1,img_2)
			psnr_mean = psnr_img + psnr_mean
	psnr_mean_agg = 2/(len(img_set)*(len(img_set)-1))*(psnr_mean)
	return psnr_mean_agg

def aggregate_Angular_PSNR(img_set):
    psnr_mean = aggregate_Mean_PSNR(img_set)
    psnr_angular = 1/(img_set[0].shape[0]*img_set[0].shape[1]) * psnr_mean
    return psnr_angular
	
def SSIM(original, compressed): 
	original_np = np.squeeze(original)
	compressed_np = np.squeeze(compressed)
	ssim_noise = ssim(original_np, compressed_np, channel_axis=-1)
	return ssim_noise

def mean_SSIM(img_reference,img_set):
	psnr_mean = 0
	for img in img_set:
		psnr_img = SSIM(img_reference,img)
		psnr_mean = psnr_img + psnr_mean
	return 1/(len(img_set))*(psnr_mean)

def angular_SSIM(img_set):
    img_center = image_Center(img_set=img_set)
    psnr_mean = mean_SSIM(img_center,img_set)
    psnr_angular = 1/(img_center.shape[0]*img_center.shape[1]) * psnr_mean
    return psnr_angular

def brisque_Mean(img_set):
	mean = 0 
	br=BRISQUE(False)
	for img in img_set:
		mean = mean + br.score(img)
	return mean/(len(img_set))
	
	
def image_Center(img_set):
	shape = len(img_set)
	s_0=ceil(shape/2)
	return img_set[s_0]

def main(): 
	path = r'C:\Users\gabri\OneDrive\Documenti\UniTO-DOCS\Stage\datasets\LytroIllum_Dataset_INRIA_SIROCCO\Data\ChezEdgar\viewpoints_13px'
	img_set = load_images(path)
	value = angular_PSNR(img_set) 
	print(f"PSNR value is {value} dB") 
	value_SSIM = angular_SSIM(img_set) 
	print(f"SSMI value is {value_SSIM} dB") 
	value_AGG_SSIM = aggregate_Angular_PSNR(img_set)
	print(f"AGG SSIM value is {value_AGG_SSIM} dB")
	value_BRISQUE = brisque_Mean(img_set)
	print(f"BRISQUE value is {value_BRISQUE} dB")
	
	
if __name__ == "__main__": 
	main() 
