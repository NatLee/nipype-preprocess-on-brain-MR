from matplotlib import pyplot as plt
import numpy as np

from nilearn import image
from nilearn.plotting import plot_stat_map
import nibabel as nib


def draw_segmentation(input_nii_path:str, input_seg_nii_path:str, output_png_path:str, threshold:float=0.6, title='Prob. map'):
    input_nii = image.smooth_img(input_nii_path, fwhm=None)
    intput_seg_nii = image.smooth_img(input_seg_nii_path, fwhm=None)
    
    # Normalize the segmentation image data to 0-1
    data = intput_seg_nii.get_fdata()
    normalized_data = (data - np.min(data)) / (np.max(data) - np.min(data))
    
    # Create a new NIfTI image with the normalized data
    normalized_intput_seg_nii = nib.Nifti1Image(normalized_data, intput_seg_nii.affine, intput_seg_nii.header)
      
    plot_stat_map(
        stat_map_img=normalized_intput_seg_nii,
        title=title,
        cmap=plt.cm.magma,
        threshold=threshold,
        bg_img=input_nii, # bg_img is the background image on top of which we plot the stat_map
        display_mode='z',
        cut_coords=range(-50, 50, 20),
        dim=-1,
        output_file=output_png_path
    )