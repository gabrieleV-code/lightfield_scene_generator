import cv2
import numpy as np
from skimage import img_as_float
from brisque import BRISQUE
from skimage.color import rgb2gray
import torch
import torchvision.transforms as transforms
import cv2
import numpy as np
#from piq import niqe

def load_lenslet_image(image_path):
    """Carica un'immagine PNG che rappresenta un lenslet light field"""
    return np.asarray(cv2.imread(image_path))

def extract_sub_apertures(lenslet_image, grid_size=(8, 8)):
    """Estrae le sub-aperture da un'immagine lenslet PNG"""
    H, W, _ = lenslet_image.shape
    grid_H, grid_W = grid_size
    patch_H, patch_W = H // grid_H, W // grid_W  # Dimensione di ogni sub-apertura

    sub_apertures = []
    for i in range(grid_H):
        for j in range(grid_W):
            patch = lenslet_image[i * patch_H:(i + 1) * patch_H, j * patch_W:(j + 1) * patch_W]
            sub_apertures.append(patch)

    return sub_apertures


def calculate_niqe(image):
    """Calcola NIQE usando la libreria PIQ"""
    transform = transforms.ToTensor()
    image_tensor = transform(image).unsqueeze(0)  # Aggiungi batch dimension
    niqe_score = niqe(image_tensor)
    return niqe_score.item()

def calculate_metrics(image):
    """Calcola BRISQUE e NIQE su un'immagine"""
    obj = BRISQUE(url=False)
    arr = np.array(image)
    brisque_score = obj.score(arr)
    gray_image = rgb2gray(img_as_float(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)))
    #niqe_score = niqe(gray_image)
    #niqe_score=calculate_niqe(image)
    return brisque_score,0#, niqe_score

# --- Caricamento e Decodifica Light Field Lenslet ---
lenslet_image = load_lenslet_image(r"C:\Users\gabri\OneDrive\Documenti\UniTO-DOCS\Stage\LightfieldsRenderer\Lightfield_001\Lenslets\LF_Scene_0_lf_0_lenslet.png")
sub_apertures = extract_sub_apertures(lenslet_image, grid_size=(16, 16))  # Cambia 8x8 se necessario

# --- Valutazione sulla vista centrale ---
center_idx = len(sub_apertures) // 2
brisque_central, niqe_central = calculate_metrics(sub_apertures[center_idx])

# --- Valutazione su tutte le sub-aperture (media) ---
brisque_scores, niqe_scores = [], []
for img in sub_apertures:
    b_score, n_score = calculate_metrics(img)
    brisque_scores.append(b_score)
    niqe_scores.append(n_score)

brisque_avg = np.mean(brisque_scores)
niqe_avg = np.mean(niqe_scores)

# --- Risultati ---
print(f"BRISQUE (Vista Centrale): {brisque_central:.2f}")
print(f"NIQE (Vista Centrale): {niqe_central:.2f}")
print(f"BRISQUE (Media su Light Field): {brisque_avg:.2f}")
print(f"NIQE (Media su Light Field): {niqe_avg:.2f}")
