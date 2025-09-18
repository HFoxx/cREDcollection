from PIL import Image
import numpy as np
from scipy.ndimage import sobel, gaussian_laplace
from numpy.fft import fft2, fftshift
"""
            print(calculate_sharpness(np.array(img)))
            print(calculate_laplacian_sharpness(img))
            print(calculate_fourier_sharpness(img))
"""
def calculate_sharpness(image):
    dx = sobel(image, axis=0, mode='constant')
    dy = sobel(image, axis=1, mode='constant')
    sobel_image = np.hypot(dx, dy)
    sharpness = np.mean(sobel_image)
    return sharpness


def calculate_laplacian_sharpness(image):
    laplacian = gaussian_laplace(image, sigma=1)
    sharpness = np.abs(laplacian).mean()
    return sharpness

def calculate_variance_sharpness(image):
    sharpness = np.var(image)
    return sharpness


def calculate_fourier_sharpness(image):
    f_transform = fftshift(fft2(image))
    magnitude_spectrum = 20*np.log(np.abs(f_transform))
    sharpness = np.mean(magnitude_spectrum)
    return sharpness
