import os
import re
from PIL import Image
import numpy as np

# Dimensioni delle immagini
W, H = 625, 434  # Sostituisci con le dimensioni reali delle immagini
F_x,F_y = 16,16 
# Cartella contenente le immagini
def descend_folder(main_path,array_paths):
    descend_path = main_path
    for dir in os.listdir(main_path):
        dir_path = os.path.join(main_path,dir)  
        if(dir == "png"):
            array_paths.append(dir_path)
            return array_paths
        if os.path.isdir(dir_path):
            array_paths = descend_folder(dir_path,array_paths)
    return array_paths

def gen_lenslet(image_folder,save_folder):
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
                    im=image_mat[x, y][i]
                    final_image[i * N + x, j * M + y] = image_mat[x, y][i, j]

    # Visualizza l'immagine finale (convertita in formato PIL)
    final_image_pil = Image.fromarray(final_image)
    final_image_pil.show()

    # Salva l'immagine finale
    final_image_pil.save(save_folder)

def lenslet(image_folder):
    lenslet_folder = os.path.abspath(os.path.join(image_folder, '..//..'))
    lf_names = lenslet_folder.split('\\')
    lf_name = lf_names[len(lf_names)-1]
    lf_scene_name = lf_names[len(lf_names)-2]
    save_folder = os.path.abspath(os.path.join(lenslet_folder, lf_scene_name+"_"+lf_name + '_lenslet.png'))
    gen_lenslet(image_folder,save_folder)


def multiple_lenslets(starting_directory):
    paths = descend_folder(starting_directory,[])
    for path in paths:
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
            """ parts = image_file.split('_')
            x = int(parts[4])
            y = int(parts[7].split('.')[0])
            max_x = max(max_x, x)
            max_y = max(max_y, y)
            image_positions.append((x, y, image_file)) """
            image_positions.append((x, y, image_file))

    """ N = max_x + 1
    M = max_y + 1 """

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


image_folders = r'C:\Users\gabri\OneDrive\Documenti\UniTO-DOCS\Stage\LightfieldsRenderer\Lightfield_more_006\LF_Scene_27'  # Sostituisci con il percorso reale delle immagini
#folders = os.listdir(image_folders)
#for image_folder in folders:
#lenslet(image_folder)
#    multiple_lenslets(os.path.join(image_folders,image_folder))
multiple_lenslets(image_folders)
folder_to_reach = r'C:\Users\gabri\OneDrive\Documenti\UniTO-DOCS\Stage\LightfieldsRenderer\Lightfield_002'
move_lightfields(folder_to_reach,image_folders)