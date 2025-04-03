from PIL import Image
from PIL import ImageChops
import torchvision.transforms.functional as F
import torch
import os
from lensletRearrange import multiview2lenslet
import add_vignette

def compareImages(first,second):
    image1 = Image.open(first)
    image2 = Image.open(second)

    diff = ImageChops.difference(image1, image2)
    diff.show()
    diff.save(r'C:\Users\gabri\OneDrive\Documenti\UniTO-DOCS\Stage\LightfieldsRenderer\Lightfield_more_006\LF_Scene_27\lf_0\Lenslets_13\diff.png')

    channels = diff.split()
    for channel in channels:
        if channel.getbbox() is not None:
            print("images are different")
            return;
    print("images are the same")

def thirteen2sixteenViews(png_file_path, output_image_path):
    # Define the dimensions of the square cut
    

    # Define the starting and ending coordinates for the square cut
    start_x, start_y = 4152, 520
    #end_x, end_y = start_x + cut_width, start_y + cut_height

    # Open the PNG file using PIL
    image = Image.open(png_file_path)
    cut_width, cut_height = int(image.size[0]/13), int(image.size[1]/13)
    print(cut_width,cut_height)

    image = F.pil_to_tensor(image)
    #image = image.to("cuda")
    newImage = image.clone()
    #print(image.shape)

    #two top left views
    #0,1 to 00
    newImage[:, :cut_height, :cut_width ] = image[:, cut_height:cut_height*2, :cut_width]
    #2,0 to 00
    newImage[:, :cut_height, cut_width:cut_width*2 ] = image[:, :cut_height, cut_width*2:cut_width*3]

    #two top right views
    #10,0 to 11,0
    newImage[:, :cut_height, cut_width*11:cut_width*12 ] = image[:, :cut_height,cut_width*10:cut_width*11]
    #12,1 to 12,0
    newImage[:, :cut_height, cut_width*12:cut_width*13 ] = image[:, cut_height*2:cut_height*3, cut_width*12:cut_width*13]

    #two down left views
    #0,12 to 0,13
    newImage[:, cut_height*12:cut_height*13, :cut_width] = image[:, cut_height*11:cut_height*12, :cut_width]
    #2,13 to 1,13
    newImage[:, cut_height*12:cut_height*13, cut_width:cut_width*2 ] = image[:, cut_height*12:cut_height*13, cut_width*2:cut_width*3]

    #two down right views
    #10,13 to 11,13
    newImage[:, cut_height*12:cut_height*13, cut_width*11:cut_width*12 ] = image[:, cut_height*12:cut_height*13,cut_width*10:cut_width*11]
    #13,12 to 13,13
    newImage[:,cut_height*12:cut_height*13, cut_width*12:cut_width*13 ] = image[:, cut_height*11:cut_height*12, cut_width*12:cut_width*13]



    #create bigger tensor for extra views
    lf16 = torch.zeros(newImage.shape[0], newImage.shape[1]+cut_height*3, newImage.shape[2]+cut_width*3, dtype=torch.int8)
    #lf16 = lf16.to("cuda")

    #copy all original views
    lf16[:, cut_height:newImage.shape[1]+cut_height, cut_width:newImage.shape[2]+cut_width] = newImage[:, :, :]
    #copy first column
    lf16[:, cut_height:newImage.shape[1]+cut_height, :cut_width] = newImage[:, :, cut_width:cut_width*2]
    #copy 15 column
    lf16[:, cut_height:newImage.shape[1]+cut_height, newImage.shape[2]+cut_width:newImage.shape[2]+cut_width*2] = newImage[:, :, newImage.shape[2]-cut_width:]
    #copy 16 column
    lf16[:, cut_height:newImage.shape[1]+cut_height, newImage.shape[2]+cut_width*2:newImage.shape[2]+cut_width*3] = newImage[:, :, newImage.shape[2]-cut_width:]

    #copy first row
    lf16[:, :cut_height, :] = lf16[:, cut_height:cut_height*2, :] 
    #copy 15 row
    lf16[:, newImage.shape[1]+cut_height:newImage.shape[1]+cut_height*2, :] = lf16[:, newImage.shape[1]-cut_height:newImage.shape[1], :]
    #copy 16 row
    lf16[:, newImage.shape[1]+cut_height*2:newImage.shape[1]+cut_height*3, :] = lf16[:, newImage.shape[1]-cut_height:newImage.shape[1], :]




    # Save the resulting image
    lf16 = F.to_pil_image(lf16, mode="RGB")
    lf16.save(output_image_path)

    #newImage = F.to_pil_image(newImage)
    #newImage.save('/home/machado/New_Extracted_Dataset/head2_anky-1_13.png')
#
# Example usage:
#png_file_path = '/home/machado/New_Extracted_Dataset/EPFL/MultiView_RGB/Buildings/Pillars.png'
#output_image_path = '/home/machado/New_Extracted_Dataset/head2_anky-1_15.png'
#thirteen2sixteenViews(png_file_path, output_image_path)


from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

ds_path = r'C:\Users\gabri\OneDrive\Documenti\UniTO-DOCS\Stage\LightfieldsRenderer\Lightfield_more_006\LF_Scene_27\lf_0\Lenslets_13'
output_path = r'C:\Users\gabri\OneDrive\Documenti\UniTO-DOCS\Stage\LightfieldsRenderer\Lightfield_more_006\LF_Scene_27\lf_0\Lenslets_13\Multiview_16x16'
#for rearange
pathOut=r"C:\Users\gabri\OneDrive\Documenti\UniTO-DOCS\Stage\LightfieldsRenderer\Lightfield_more_006\LF_Scene_27\lf_0\Lenslets_13\Lenslet_16x16_RGB"
pathOutg= r'C:\Users\gabri\OneDrive\Documenti\UniTO-DOCS\Stage\LightfieldsRenderer\Lightfield_more_006\LF_Scene_27\lf_0\Lenslets_13\Lenslet_16x16_Gscale'

for classe in os.listdir(ds_path):
    if "_2.png" in classe:
        classe_out = os.path.join(output_path,classe)
        os.makedirs(output_path, exist_ok=True)
        os.makedirs(pathOut, exist_ok=True)
        os.makedirs(pathOutg, exist_ok=True)
            #for lf in os.listdir(os.path.join(ds_path,classe)):
            
        lf_in = os.path.join(ds_path, classe)
        lf_16_out = classe_out
        #print(lf)
        print(lf_16_out)
     

        compareImages(lf_in,r'C:\Users\gabri\OneDrive\Documenti\UniTO-DOCS\Stage\LightfieldsRenderer\Lightfield_more_006\LF_Scene_27\lf_0\LFPlane.001\combined_image_cut_13.png')
        thirteen2sixteenViews(lf_in, lf_16_out)
        compareImages(lf_16_out,r'C:\Users\gabri\OneDrive\Documenti\UniTO-DOCS\Stage\LightfieldsRenderer\Lightfield_more_006\LF_Scene_27\lf_0\LFPlane.001\combined_image_13.png')
        #multiview2lenslet(lf_16_out, os.path.join(pathOut,classe), os.path.join(pathOutg,classe))
