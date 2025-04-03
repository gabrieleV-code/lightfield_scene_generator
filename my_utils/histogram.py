import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

def save_hsv_value_histogram(image_path, output_histogram_path):
    # Load the image
    image = cv2.imread(image_path)

    # Convert the image to HSV color space
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Extract the Value (V) channel
    v_channel = hsv_image[:, :, 2]

    # Compute histogram for the Value channel
    histogram, bins = np.histogram(v_channel, bins=256, range=(0, 256))

    # Plot the histogram
    plt.figure(figsize=(6, 4))
    plt.plot(histogram, color='black')
    plt.fill_between(range(256), histogram, color='gray', alpha=0.6)
    plt.xlim([0, 256])
    plt.xlabel("Value (V)")
    plt.ylabel("Frequency")
    plt.title("HSV Value Histogram")
    plt.grid(True, linestyle="--", alpha=0.5)

    # Save the histogram image
    plt.savefig(output_histogram_path)
    plt.close()

def save_luminance_histogram(image_path, output_histogram_path):
    # Load the image
    image = cv2.imread(image_path)

    # Convert the image to YCbCr color space
    ycbcr_image = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)

    # Extract the Luminance (Y) channel
    y_channel = ycbcr_image[:, :, 0]

    # Compute histogram for the Y channel
    histogram, bins = np.histogram(y_channel, bins=256, range=(0, 256))

    # Plot the histogram
    plt.figure(figsize=(6, 4))
    plt.plot(histogram, color='black')
    plt.fill_between(range(256), histogram, color='gray', alpha=0.6)
    plt.xlim([0, 256])
    plt.xlabel("Luminance (Y)")
    plt.ylabel("Frequency")
    plt.title("Luminance Histogram (Y Channel)")
    plt.grid(True, linestyle="--", alpha=0.5)

    # Save the histogram image
    plt.savefig(output_histogram_path)
    plt.close()

# Example usage
file_name = "LF_Scene_6_lf_2_lenslet.png"
image_folder = r"C:\Users\gabri\OneDrive\Documenti\UniTO-DOCS\Stage\LightfieldsRenderer\Lightfield_001\Lenslets"
image_path = os.path.join(image_folder,file_name)


output_folder = r"C:\Users\gabri\OneDrive\Documenti\UniTO-DOCS\Stage\Tesi"
hist_folder = os.path.join(output_folder,r"histograms")
if not os.path.exists(hist_folder):
    os.makedirs(hist_folder)


output_histogram_path = os.path.join(hist_folder ,f"{file_name}_hsv_value_histogram.png")  # Output histogram image path
output_luminance_histogram_path =  os.path.join(hist_folder ,f"{file_name}_luminance_histogram.png")

save_hsv_value_histogram(image_path, output_histogram_path)
#save_luminance_histogram(image_path, output_luminance_histogram_path)
print(f"Histogram saved at: {output_histogram_path}")
print(f"Luminance Histogram saved at: {output_luminance_histogram_path}")
