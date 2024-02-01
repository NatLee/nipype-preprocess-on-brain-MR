import nibabel as nib

def save_nii(data, path, affine):
    nib.save(nib.Nifti1Image(data, affine), path)
    return