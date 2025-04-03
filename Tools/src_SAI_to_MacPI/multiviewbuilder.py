import os
import re
from PIL import Image
import numpy as np


def combine_images(image_paths, rows, cols, output_path):
    """
    Combine NxM images into a single image.

    :param image_paths: List of file paths to the images (must contain rows * cols paths).
    :param rows: Number of rows in the matrix.
    :param cols: Number of columns in the matrix.
    :param output_path: Path to save the combined image.
    """
    if len(image_paths) != rows * cols:
        raise ValueError("Number of images does not match the matrix dimensions.")

    # Open all images
    images = [Image.open(path) for path in image_paths]

    # Assume all images are the same size
    img_width, img_height = images[0].size

    # Create a blank canvas for the final image
    combined_width = cols * img_width
    combined_height = rows * img_height
    combined_image = Image.new('RGB', (combined_width, combined_height))

    # Paste each image into the correct position
    for row in range(rows):
        for col in range(cols):
            index = row * cols + col
            x_offset = col * img_width
            y_offset = row * img_height
            combined_image.paste(images[index], (x_offset, y_offset))

    # Save the final image
    combined_image.save(output_path)
    print(f"Combined image saved to {output_path}")

# Example usage
if __name__ == "__main__":
    # Example: Specify the image paths and matrix dimensions
    image_folder = r"C:\Users\gabri\OneDrive\Documenti\UniTO-DOCS\Stage\LightfieldsRenderer\Lightfield_001\LFs\LF_Scene_26\lf_3\LFPlane.001\png"
    output_file = r"C:\Users\gabri\OneDrive\Documenti\UniTO-DOCS\Stage\LightfieldsRenderer\Lightfield_001\LFs\LF_Scene_26\lf_3\LFPlane.001\combined_imag.png"

    # Collect image paths
    image_files = [os.path.join(image_folder,f) for f in os.listdir(image_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    # Combine images into a 2x3 grid
    combine_images(image_files, rows=16, cols=16, output_path=output_file)