from add_vignette import multiple_lenslets as multiple_lenslets_padding
import os
import re
from PIL import Image
import numpy as np

# Dimensioni delle immagini
W, H = 622, 432  # Sostituisci con le dimensioni reali delle immagini
F_x,F_y = 16,16 
# Cartella contenente le immagini
def descend_folder(main_path,array_paths,image_dir_name):
    descend_path = main_path
    for dir in os.listdir(main_path):
        dir_path = os.path.join(main_path,dir)  
        if(dir == image_dir_name):
            array_paths.append(dir_path)
            return array_paths
        if os.path.isdir(dir_path):
            array_paths = descend_folder(dir_path,array_paths,image_dir_name=image_dir_name)
    return array_paths

def gen_lenslet(image_folder,save_folder,save_folder_jpg):
    # Carica le immagini dalla cartella e determina N e M
    image_mat, N, M = load_images(image_folder)
    # Determina il numero di canali (3 per RGB, 4 per RGBA)
    num_channels = image_mat[0, 0].shape[2] if len(image_mat[0, 0].shape) == 3 else 1

    # Creazione dell'immagine finale con risoluzione maggiore
    final_image = np.zeros((H * M,W * N, num_channels), dtype=np.uint8)

    # Popolamento dell'immagine finale con i pixel delle immagini originali
    for i in range(H):
        for j in range(W):
            for x in range(N):
                for y in range(M):
                    final_image[i * N + x, j * M + y] = image_mat[x, y][i, j]
                    #final_image[i * N + x, j * N:(j + 1) * N] = image_mat[x, y][i, j]

    # Visualizza l'immagine finale (convertita in formato PIL)
    final_image_pil = Image.fromarray(final_image)
    final_image_pil.show()

    # Salva l'immagine finale
    final_image_pil.save(save_folder)
    final_image_pil.save(save_folder_jpg)

def lenslet(image_folder,lenslet_name):
    lenslet_folder = os.path.abspath(os.path.join(image_folder, '..//..'))
    lf_names = lenslet_folder.split('\\')
    lf_name = lf_names[len(lf_names)-1]
    lf_scene_name = lf_names[len(lf_names)-2]
    save_folder = os.path.abspath(os.path.join(lenslet_folder, lf_scene_name+"_"+lf_name + f'{lenslet_name}.png'))
    save_folder_jpg = os.path.abspath(os.path.join(lenslet_folder, lf_scene_name+"_"+lf_name + f'{lenslet_name}.jpg'))
    gen_lenslet(image_folder,save_folder,save_folder_jpg=save_folder_jpg)


def multiple_lenslets(starting_directory,dir_name,lenslet_name):
    paths = descend_folder(starting_directory,[],image_dir_name=dir_name)
    for path in paths:
        print("Current image path: "+path)
        lenslet(path,lenslet_name)

def descend_folder_for_lenslet(main_path,array_paths,lenslet_name):
    for dir in os.listdir(main_path):
        dir_path = os.path.join(main_path,dir)  
        if(re.search(f'{lenslet_name}.png',dir)):
            array_paths.append(dir_path)
            return array_paths
        if os.path.isdir(dir_path):
            array_paths=descend_folder_for_lenslet(dir_path,array_paths,lenslet_name)
    return array_paths

def move_lightfields(ending_directory,directory_to_move,lenslet_name):
    ending_directory = os.path.abspath(os.path.join(ending_directory, 'Lenslets'))
    try:
        os.makedirs(ending_directory)
    except:
        print("")
    pathes = descend_folder_for_lenslet(directory_to_move,[],lenslet_name)
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
    # Qua il codice ipotizza l'immagine sia del tipo 'img_x_y.jpg'
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

    for x, y, image_file in image_positions:
        image_path = os.path.join(folder, image_file)
        img = Image.open(image_path)
        img = img.resize((W, H))  # Assicurati che tutte le immagini abbiano la stessa dimensione WxH
        image_matrix[x, y] = np.array(img)

    return image_matrix, N, M

if __name__ == "__main__":
    image_folders = r'C:\Users\gabri\OneDrive\Documenti\UniTO-DOCS\Stage\LightfieldsRenderer\Lightfield_001\LFs'  # Sostituisci con il percorso reale delle immagini
    multiple_lenslets_padding(image_folders)
    lenslet_name = "_lenslet_9952_6912"
    multiple_lenslets(image_folders,"png_cut_13",lenslet_name)
    folder_to_reach = r'C:\Users\gabri\OneDrive\Documenti\UniTO-DOCS\Stage\LightfieldsRenderer\Lenslets_Padded_9952x6912_001'
    move_lightfields(folder_to_reach,image_folders,lenslet_name)