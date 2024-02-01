import numpy as np
import nibabel as nib

def load_nii(path:str):
    nii = nib.load(path)
    return np.asanyarray(nii.dataobj), nii.affine
