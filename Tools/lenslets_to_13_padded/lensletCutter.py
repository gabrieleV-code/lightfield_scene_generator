from PIL import Image
import os

def extract_and_save_square_from_png(png_file_path, output_image_path):
    # Define the dimensions of the square cut
    cut_width, cut_height = 625*13, 434*13

    # Define the starting and ending coordinates for the square cut
    start_x, start_y = 625, 434
    end_x, end_y = start_x + cut_width, start_y + cut_height

    # Open the PNG file using PIL
    image = Image.open(png_file_path)

    # Crop the square region
    image_cropped = image.crop((start_x, start_y, end_x, end_y))

    # Save the resulting image
    image_cropped.save(output_image_path)

# Example usage:
#png_file_path = '/home/idm/New_Extracted_Dataset/EPFL/Lenslet_8x8_RGB/Studio/Ankylosaurus_&_Diplodocus_1.png'
#output_image_path = 'head2_anky-1.png'
#extract_and_save_square_from_png(png_file_path, output_image_path)
#
png_file_path = r'C:\Users\gabri\OneDrive\Documenti\UniTO-DOCS\Stage\LightfieldsRenderer\Lightfield_more_006\LF_Scene_27\lf_0\LFPlane.001'
output_image_path = os.path.join(png_file_path,'../Lenslets_13')

if not os.path.exists(output_image_path):
    os.makedirs(output_image_path)

for file in os.listdir(png_file_path):
    if file.endswith("combined_image_2.png"):
        new_input_file_path = os.path.join(png_file_path, file)
        new__output_file_path= os.path.join(output_image_path, file)
        extract_and_save_square_from_png(png_file_path=new_input_file_path,output_image_path=new__output_file_path)