from PIL import Image
import os

image_path = r""

images = os.listdir(image_path)

for image in images:
    image_path = os.path.join(image_path, image)
    img = Image.open(image_path).convert('L')
    gray_image_path = os.path.abspath(os.path.join(image_path, '..//lenslet_grey',image_path[:-5:-1]+"_gray.png"))
    img.save(image_path)



