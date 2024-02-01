import nibabel as nib

def load_nii(path:str):
    nii = nib.load(path)
    return nii.get_data(), nii.affine
