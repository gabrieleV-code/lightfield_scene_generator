import os
import re
from PIL import Image
import numpy as np

# Dimensioni delle immagini
W, H = 625, 434  # Sostituisci con le dimensioni reali delle immagini
F_x,F_y = 16,16 
# Cartella contenente le immagini
def descend_folder(main_path,array_paths,dir_name = "png"):
    descend_path = main_path
    for dir in os.listdir(main_path):
        dir_path = os.path.join(main_path,dir)  
        if(dir == dir_name):
            array_paths.append(dir_path)
            return array_paths
        if os.path.isdir(dir_path):
            array_paths = descend_folder(dir_path,array_paths,dir_name)
    return array_paths



def apply_grid_vignette(images, grid_size, output_dir, intensity=3):
    """
    Apply a vignette effect to a list of images based on their position in a grid.
    The effect varies smoothly across the grid without quantization.
    
    :param images: List of image paths in row-major order.
    :param grid_size: Tuple (rows, cols) specifying the grid dimensions.
    :param output_dir: Directory to save the modified images.
    :param intensity: Intensity of the vignette effect.
    """
    images_ = []
    for x in range(1,F_x-2):
        for y in range(1,F_y-2):
            images_.append(images[x*13 + y])

    images = images_
    rows, cols = grid_size
    single_img = Image.open(images[0])
    img_width, img_height = single_img.size

    # Total size of the composite vignette mask
    comp_width, comp_height = cols * img_width, rows * img_height

    # Create a global vignette mask
    x = np.linspace(-1, 1, comp_width)
    y = np.linspace(-1, 1, comp_height)
    xv, yv = np.meshgrid(x, y)
    vignette = np.sqrt(xv**2 + yv**2)
    vignette = (1 - (vignette / np.max(vignette)) ** intensity).clip(0, 1)

    # Process each image individually
    for row in range(rows):
        for col in range(cols):
            # Calculate the index of the current image
            idx = row * cols + col
            if idx >= len(images):
                break  # Stop if there are fewer images than grid slots

            # Open the current image
            img = Image.open(images[idx]).resize((img_width, img_height))

            # Extract the vignette region for the current image
            left = col * img_width
            upper = row * img_height
            right = left + img_width
            lower = upper + img_height
            vignette_region = vignette[upper:lower, left:right]

            # Apply the vignette effect by scaling brightness
            img_np = np.array(img, dtype=float) / 255.0  # Normalize image to [0, 1]
            img_vignetted_np = img_np * vignette_region[:, :, np.newaxis]  # Scale per channel
            img_vignetted = Image.fromarray((img_vignetted_np * 255).astype('uint8'))

            # Save the processed image
            r = f"{row:0{2}d}"
            c = f"{col:0{2}d}"
            output_path = f"{output_dir}/image_{r}_{c}.png"
            img_vignetted.save(output_path)
            print(f"Saved vignetted image to: {output_path}")

def copy_images_subset(images,grid_to_resize_to,output_dir):
    rows, cols = grid_to_resize_to

    for x in range(1,F_x-2):
        for y in range(1,F_y-2):
            img = Image.open(images[x*F_x + y])
            #im_name = images[x*F_x + y].split("\\")[-1]
            output_path = f"{output_dir}/image_{x}_{y}.png"
            img.save(output_path)

def cutdown(image_folder,output_dir):
    images = [os.path.join(image_folder,f) for f in os.listdir(image_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

    start_index = (16 - 13) // 2  # 1
    end_index = start_index + 13  # 14
    #Cut down the image number to 13x13
    if len(images)>(169):
        images_ = []
        for x in range(start_index,end_index):
            for y in range(start_index,end_index):
                img = Image.open(images[x*16 + y])
                output_path = f"{output_dir}/image_{x}_{y}.png"
                img.save(output_path)



def padding(image_folder,output_dir):
    # Calculate start and end indices for the 13x13 grid placement
    images = [os.path.join(image_folder,f) for f in os.listdir(image_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

    start_index = (16 - 13) // 2  # 1
    end_index = start_index + 13  # 14
    #Cut down the image number to 13x13
    if len(images)>(169):
        images_ = []
        for x in range(start_index,end_index):
            for y in range(start_index,end_index):
                images_.append(images[x*F_x + y])

        images = images_
   

    # Reshape the array into a 16x16 matrix
    #matrix = images.reshape(16, 16)

    # Extract the 13x13 submatrix (from the second row and column)
    #matrix_13x13 = matrix[1:14, 1:14]

    #matrix_13x13 = np.full((16, 16), None, dtype=object)
    """ for x in range(1,F_x-2):
        for y in range(1,F_y-2):
            img = Image.open(images[x*F_x + y]) """
    #matrix_13x13 = matrix_13x13[1:F_x-2,1:F_y-2]

    matrix_13x13 = np.full((13, 13), None, dtype=object)
    for x in range(13):
        for y in range(13):
            img = Image.open(images[x*13 + y])
            img = img.crop((1,1,623,433))
            matrix_13x13[x][y]=img

    matrix_16x16 = np.full((16, 16), None, dtype=object)
    # Place the 13x13 matrix in the center of the 16x16 grid
    matrix_16x16[start_index:end_index, start_index:end_index] = matrix_13x13

    # Copy borders to the extra rows/columns
    # Top and bottom rows
    matrix_16x16[start_index - 1, start_index:end_index] = matrix_13x13[0, :]    # Top row
    matrix_16x16[end_index, start_index:end_index] = matrix_13x13[(F_x-4), :]         # Bottom row
    matrix_16x16[end_index+1, start_index:end_index] = matrix_13x13[(F_x-4), :]         # Second bottom row


    # Left and right columns
    matrix_16x16[start_index:end_index, start_index - 1] = matrix_13x13[:, 0]    # Left column
    
    # Left and right columns
    matrix_16x16[start_index:end_index, end_index] = matrix_13x13[:, F_y-4]         # Right column
    matrix_16x16[start_index:end_index, end_index+1] = matrix_13x13[:, F_y-4]         # Second right column

    matrix_16x16[start_index - 1, end_index:end_index+2] = matrix_16x16[start_index, end_index:end_index+2]    # Top right row
    matrix_16x16[start_index - 1, 0] = matrix_16x16[start_index-1, 1]    # Top Left row

    matrix_16x16[end_index: end_index+2, end_index] = matrix_16x16[end_index: end_index+2, end_index-1]   # Bottom right row
    matrix_16x16[end_index: end_index+2, end_index+1] = matrix_16x16[end_index: end_index+2, end_index-1]   # Bottom right row

    matrix_16x16[end_index, start_index-1] = matrix_16x16[end_index-1, start_index-1]         # Bottom row
    matrix_16x16[end_index+1, start_index-1] = matrix_16x16[end_index-1, start_index-1] 
    
    
    black_image = Image.new("RGB", matrix_13x13[0][0].size, color=(0, 0, 0))

    for x in range(16):
        for y in range(16):
            r = f"{x:0{2}d}"
            c = f"{y:0{2}d}"
            output_path = f"{output_dir}/lf_{r}_{c}.png"
            if matrix_16x16[x][y]:
                matrix_16x16[x][y].save(output_path) 
            else:
                black_image.save(output_path)

def lenslet(image_folder):
    lenslet_folder = os.path.abspath(os.path.join(image_folder, '..'))
    save_folder = os.path.abspath(os.path.join(lenslet_folder,"png_cut_13"))
    #save_folder = os.path.abspath(os.path.join(lenslet_folder,"png_13"))
    #save_folder_ = save_folder
    image_files = [os.path.join(image_folder,f) for f in os.listdir(image_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    #if not os.path.exists(save_folder_cut):
    #    os.makedirs(save_folder_cut)
    
    #cutdown(image_folder,save_folder_cut)
    padding(image_folder,save_folder)
    #copy_images_subset(images=image_files,grid_to_resize_to=(13,13),output_dir=save_folder)
    

    """  #image_folder = save_folder
    save_folder = os.path.abspath(os.path.join(lenslet_folder,"vignette"))
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    #gen_vignette(image_folder,save_folder)
    image_files = [os.path.join(image_folder,f) for f in os.listdir(image_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    apply_grid_vignette(images=image_files,grid_size=(13,13),output_dir=save_folder)   """ 

    
    #copy(save_folder,save_folder_)


def multiple_lenslets(starting_directory):
    paths = descend_folder(starting_directory,[],"png")
    for path in paths:
        print("Adding padding to "+path)
        lenslet(path)

def descend_folder_for_lenslet(main_path,array_paths):
    for dir in os.listdir(main_path):
        dir_path = os.path.join(main_path,dir)  
        if(re.search('_lenslet.png',dir)):
            array_paths.append(dir_path)
            return array_paths
        if os.path.isdir(dir_path):
            array_paths=descend_folder_for_lenslet(dir_path,array_paths)
    return array_paths

def move_lightfields(ending_directory,directory_to_move):
    ending_directory = os.path.abspath(os.path.join(ending_directory, 'Lenslets'))
    try:
        os.makedirs(ending_directory)
    except:
        print("")
    pathes = descend_folder_for_lenslet(directory_to_move,[])
    for file_path in pathes:
        img = Image.open(file_path).convert('L')
        lf_names = file_path.split('\\')
        lf_name = lf_names[len(lf_names)-1]
        img.save(os.path.join(ending_directory,lf_name))
        #os.system('copy '+file_path +' '+ os.path.join(ending_directory,lf_name))


def load_images(folder):
    image_files = [f for f in os.listdir(folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    image_positions = []

    # Determina N e M dinamicamente
    max_x, max_y = -1, -1
    # Qua il codice ipotizza l'immagine essere del tipo 'img_x_y.jpg'
    # Se il nome delle immagini ha un formato differente bisogna modificare qua.
    # x ed y sono dei valori interi che vanno da 0 ad N/M
        # Estrarre x e y dai nomi dei file
    for x in range(F_x):
        for y in range(F_y):
            image_file = image_files[x*F_x + y]
            image_positions.append((x, y, image_file))


    N = F_x
    M = F_y

    # Creazione della matrice per salvare le immagini
    image_matrix = np.empty((N, M), dtype=object)
    image_names_matrix = np.empty((N, M), dtype=object)

    for x, y, image_file in image_positions:
        image_path = os.path.join(folder, image_file)
        img = Image.open(image_path)
        img = img.resize((W, H))  # Assicurati che tutte le immagini abbiano la stessa dimensione WxH
        image_matrix[x, y] = np.array(img)
        image_names_matrix[x,y] = image_file

    return image_matrix, N, M,image_names_matrix

if __name__ == "__main__":
    image_folders = r'C:\Users\gabri\OneDrive\Documenti\UniTO-DOCS\Stage\LightfieldsRenderer\Lightfield_001'  # Sostituisci con il percorso reale delle immagini
    #multiple_lenslets(image_folders)
    paths = descend_folder(image_folders,[],"png_cut_13")
    for directory in paths:
        for filename in os.listdir(directory):
            if filename.startswith("image") and filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp")):
                file_path = os.path.join(directory, filename)
                try:
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
#folders = os.listdir(image_folders)
#for image_folder in folders:
#lenslet(image_folder)
#    multiple_lenslets(os.path.join(image_folders,image_folder))
#folder_to_reach = r'C:\Users\gabri\OneDrive\Documenti\UniTO-DOCS\Stage\LightfieldsRenderer\Lightfield_002'
#move_lightfields(folder_to_reach,image_folders)