import nibabel as nib
import matplotlib.pyplot as plt

from loguru import logger

from utils.load_nii import load_nii

def save_nii_as_png(nii_path, png_path):
    """
    Save a slice of a NIfTI file as a PNG image.

    Args:
    nii_path (str): Path to the NIfTI file.
    png_path (str): Path where the PNG file will be saved.
    """

    # Load the NIfTI file
    data, _ = load_nii(nii_path)

    # The data shape should be (slice_index, w, h, channels)

    # Get the middle slice
    slice_index = data.shape[0] // 2

    # Get the slice
    selected_slice = data[slice_index, :, :]
    selected_slice = selected_slice.squeeze()

    # Save the slice as a PNG file
    plt.imshow(selected_slice.T, cmap="gray", origin="lower")
    plt.axis('off')
    plt.savefig(png_path, bbox_inches='tight', pad_inches=0)
    plt.close()

    logger.info(f"Saved PNG file to {png_path}")
