import math
import os
from os import listdir
from os.path import isfile, join
from matplotlib import pyplot as plt
import numpy
import cv2
import numpy as np
import scipy


def load_images(mypath):
    onlyfiles = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]
    images = numpy.empty(len(onlyfiles), dtype=object)
    for n in range(0, len(onlyfiles)):
        images[n] = cv2.imread( join(mypath,onlyfiles[n]) )
    return images

def create_patches(image, patch_size):
    """
    Crops patches of size patch_size x patch_size from the input image.

    Args:
    - image (numpy array): The input image (2D or 3D array).
    - patch_size (int): The size of the square patch.

    Returns:
    - patches (list of numpy arrays): List containing the cropped patches.
    """
    patches = []
    height, width = image.shape[:2]  # assuming the image is either HxW or HxWxC

    # Slide a window across the image to extract patches
    for i in range(0, height, patch_size):
        for j in range(0, width, patch_size):
            patch = image[i:i + patch_size, j:j + patch_size]
            patches.append(patch)
    return patches       


def rebuild_image(patches,patch_size,image):
    height, width, channels = image.shape
    height = height//2
    width =  width//2
    rebuilt_image = np.zeros((height, width, channels), dtype=patches[0].dtype)
    patch_idx = 0

    for i in range(0,  height, patch_size):
        for j in range(0, width, patch_size):
            t=rebuilt_image[i:i + patch_size, j:j + patch_size,:]
            k= patches[patch_idx]
            rebuilt_image[i:i + patch_size, j:j + patch_size,:] = patches[patch_idx]
            patch_idx += 1

    return rebuilt_image
    

def bicubic_downsample(image, factor):
    """
    Downsamples the image using bicubic interpolation.

    Args:
    - image (numpy array): The input image.
    - factor (int): The downsampling factor.

    Returns:
    - downsampled_image (numpy array): The downsampled image.
    """
    height, width = image.shape[:2]
    new_height, new_width = height // factor, width // factor
    
    downsampled_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
    return downsampled_image

def preprocess_images(images):
    new_images = []
    for i in range(0,len(images)):
        
        image = images[i]
        height, width = image.shape[:2]
        factor = 64
        new_height, new_width = int(math.ceil(height / factor)*64), int(np.ceil(width / factor)*64)
        #image[width:new_width+width,height:new_height+height] = 0
        image_padded = np.pad(image,[(0,new_height-height),(0,new_width-width),(0,0)],mode="constant")
        patches = np.array(create_patches(image_padded,64))
        #image = np.array([images[i]])
        #patches = tf.compat.v1.extract_image_patches(image,[1,64,64,1],[1,64,64,1], rates=[1, 1, 1, 1],padding='SAME')
        #patches = np.array(patches)
        downsampled_patches = []
        for p in range(0,len(patches)):
            d_patch = bicubic_downsample(patches[p],2)
            downsampled_patches.append(d_patch)
        new_im = rebuild_image(patches=np.array(downsampled_patches),patch_size=32,image=image_padded)
        new_images.append(new_im)
    return new_images


def build_lightfiled_MacPI(images):
    if len(images)<1:
        raise Exception("Not enough images")
    
    n_imgs = len(images)
    w,h,c =images[0].shape
    m_w = n_imgs * w
    m_h = n_imgs * h
    m_image = np.zeros((m_w,m_h,c),np.uint8)

    block_size = math.ceil(math.sqrt(n_imgs))
    for i in range(0,w):
        for j in range(0,h):
            block_i = block_size*i 
            block_j = block_size*j
            for im in range(0,n_imgs):
                    block_i_ = math.floor(im/block_size)
                    block_j_ = im%block_size
                    m_image[block_i+block_i_*block_size][block_j+block_j_] = images[im][i][j]
    return m_image

def build_lightfield_MacPI_2(images):
    if len(images)<1:
        raise Exception("Not enough images")

    n_imgs = len(images)
    w,h,c =images[0].shape
    block_size = math.ceil(math.sqrt(n_imgs))
    m_w = block_size * w
    m_h = block_size * h
    m_image = np.zeros((m_w,m_h,c),np.uint8)

    for i in range(0,m_w - block_size+1,block_size):
        for j in range(0,m_h - block_size+1,block_size):
            block = images[:,i//block_size,j//block_size,:]
            block = np.reshape(block,(block_size,block_size,c))
            m_image[i:i+block_size,j:j+block_size] = block
            #display_image(m_image,title="Test2")
    return m_image


def display_image(image, title):
    """
    Displays a single image.
    
    Parameters:
    - image: np.array, the image to display.
    - title: str, the title of the image.
    """
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    plt.figure(figsize=(6, 6))
    plt.title(title)
    plt.imshow(image_rgb)
    plt.axis('off')
    plt.show()

# Example usage
folder_path = r"C:\Users\gabri\OneDrive\Documenti\UniTO-DOCS\Stage\LightfieldsRenderer\objaverse_lightfields\objaverse_multi_objects_good_geometry\LFPlane.001\png"
macro_pixel_size = 10  # Adjust macro-pixel size as needed

images = load_images(folder_path)
new_images = preprocess_images(images=images)

new_images = np.array(new_images)
display_image(image=new_images[0],title="Test")
macro_pixel_image = build_lightfield_MacPI_2(new_images)
#display_image(macro_pixel_image, "Macro-Pixel Image from Multiple Images")
display_image(macro_pixel_image,title="")
#cv2.imwrite(os.path.join(os.path.dirname(folder_path),"macppi.png"), macro_pixel_image)