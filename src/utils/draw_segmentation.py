from nilearn import image
from nilearn.plotting import plot_stat_map
from matplotlib import pyplot as plt

def draw_segmentation(input_nii_path:str, input_seg_nii_path:str, output_png_path:str, title='Prob. map'):
    input_nii = image.smooth_img(input_nii_path, fwhm=None)
    intput_seg_nii = image.smooth_img(input_seg_nii_path, fwhm=None)
    plot_stat_map(
        stat_map_img=intput_seg_nii,
        title=title,
        cmap=plt.cm.magma,
        threshold=0.3,
        bg_img=input_nii, # bg_img is the background image on top of which we plot the stat_map
        display_mode='z',
        cut_coords=range(-30, 50, 20),
        dim=-1,
        output_file=output_png_path
    )