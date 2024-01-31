import tempfile
from pathlib import Path
import shutil
import subprocess
from pathlib import Path
import os
from loguru import logger
#from multiprocessing import Pool, cpu_count

import matplotlib.pyplot as plt

from nipype.interfaces.ants.segmentation import N4BiasFieldCorrection
from nilearn.plotting import plot_anat

from scipy.signal import medfilt
from sklearn.cluster import KMeans

import numpy as np
import nibabel as nib

def showImg(img, title):
    plot_anat(img, title=title, display_mode='ortho', dim=-1, draw_cross=False, annotate=False)
    plt.savefig(title + '.png')


def plotMiddle(data, slice_no=None):
    if not slice_no:
        slice_no = data.shape[-1] // 2
    plt.figure()
    plt.imshow(data[..., slice_no], cmap="gray")
    plt.savefig('middle.png')
    return

def run_acpc_detect(nii_file: str, acpc_detect_path: str) -> Path:
    logger.info('ACPC detection on: {}'.format(nii_file))

    # Convert `nii_file` to a Path object
    nii_file_path = Path(nii_file)

    # Use a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)

        # Copy the .nii file to the temporary directory
        temp_nii_file_path = temp_dir_path / nii_file_path.name
        shutil.copy(nii_file, temp_nii_file_path)

        # Modify the command to use the new .nii file path in the temporary directory
        command = [acpc_detect_path, "-no-tilt-correction", "-center-AC", "-nopng", "-noppm", "-i", str(temp_nii_file_path)]
        
        # Run the command
        subprocess.call(command, stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)
        
        # Create a folder as the same name as the .nii file
        output_folder = nii_file_path.parent / nii_file_path.stem / 'acpc'
        Path(output_folder).mkdir(parents=True, exist_ok=True)

        # Move the output files to the folder
        for file in temp_dir_path.glob('*'):
            shutil.move(file, output_folder)

        # Use Path to change mode of the folder (include all files)
        (output_folder.parent).chmod(0o777)

    return output_folder


def orient2std(src_path, dst_path):
    command = ["fslreorient2std", src_path, dst_path]
    subprocess.call(command)
    return

def registration(src_path, dst_path, ref_path):
    command = ["flirt", "-in", src_path, "-ref", ref_path, "-out", dst_path,
               "-bins", "256", "-cost", "corratio", "-searchrx", "0", "0",
               "-searchry", "0", "0", "-searchrz", "0", "0", "-dof", "12",
               "-interp", "spline"]
    subprocess.call(command, stdout=open(os.devnull, "r"), stderr=subprocess.STDOUT)
    return

def bet(src_path, dst_path, frac=0.5):
    command = ["bet", src_path, dst_path, "-R", "-f", str(frac), "-g", "0"]
    subprocess.call(command)
    return

def bias_field_correction(src_path, dst_path):
    logger.info('N4ITK on: {}'.format(src_path))
    try:
        n4 = N4BiasFieldCorrection()
        n4.inputs.input_image = src_path
        n4.inputs.output_image = dst_path

        n4.inputs.dimension = 3
        n4.inputs.n_iterations = [100, 100, 60, 40]
        n4.inputs.shrink_factor = 3
        n4.inputs.convergence_threshold = 1e-4
        n4.inputs.bspline_fitting_distance = 300
        n4.run()
    except RuntimeError:
        logger.warning('Failed on: {}'.format(src_path))

    return

def load_nii(path):
    nii = nib.load(path)
    return nii.get_data(), nii.affine

def save_nii(data, path, affine):
    nib.save(nib.Nifti1Image(data, affine), path)
    return

def denoise(volume, kernel_size=3):
    return medfilt(volume, kernel_size)

def rescale_intensity(volume, percentils=[0.5, 99.5], bins_num=256):
    obj_volume = volume[np.where(volume > 0)]
    min_value = np.percentile(obj_volume, percentils[0])
    max_value = np.percentile(obj_volume, percentils[1])

    if bins_num == 0:
        obj_volume = (obj_volume - min_value) / (max_value - min_value).astype(np.float32)
    else:
        obj_volume = np.round((obj_volume - min_value) / (max_value - min_value) * (bins_num - 1))
        obj_volume[np.where(obj_volume < 1)] = 1
        obj_volume[np.where(obj_volume > (bins_num - 1))] = bins_num - 1

    volume = volume.astype(obj_volume.dtype)
    volume[np.where(volume > 0)] = obj_volume

    return volume

def equalize_hist(volume, bins_num=256):
    obj_volume = volume[np.where(volume > 0)]
    #hist, bins = np.histogram(obj_volume, bins_num, normed=True)
    hist, bins = np.histogram(obj_volume, bins_num)
    cdf = hist.cumsum()
    cdf = (bins_num - 1) * cdf / cdf[-1]

    obj_volume = np.round(np.interp(obj_volume, bins[:-1], cdf)).astype(obj_volume.dtype)
    volume[np.where(volume > 0)] = obj_volume
    return volume

def enhance(src_path, dst_path, kernel_size=3,
            percentils=[0.5, 99.5], bins_num=256, eh=True):
    logger.info('Preprocess on: {}'.format(src_path))
    try:
        volume, affine = load_nii(src_path)
        volume = denoise(volume, kernel_size)
        volume = rescale_intensity(volume, percentils, bins_num)
        if eh:
            volume = equalize_hist(volume, bins_num)
        save_nii(volume, dst_path, affine)
    except RuntimeError:
        logger.warning('Failed on: {}'.format(src_path))

def extract_features(data):
    x_idx, y_idx, z_idx = np.where(data > 0)
    features = []
    for x, y, z in zip(x_idx, y_idx, z_idx):
        features.append([data[x, y, z], x, y, z])
    return np.array(features)

def kmeans_cluster(data, n_clusters):
    features = extract_features(data)
    intensities = features[..., 0].reshape((-1, 1))
    kmeans_model = KMeans(n_clusters=n_clusters, init="k-means++",
                          precompute_distances=True, verbose=0,
                          random_state=7, n_jobs=1,
                          max_iter=1000, tol=1e-6).fit(intensities)

    labels = np.zeros(data.shape)
    for l, f in zip(kmeans_model.labels_, features):
        labels[int(f[1]), int(f[2]), int(f[3])] = l + 1

    return labels

def get_target_label(labels, data):
    labels_set = np.unique(labels)
    mean_intensities = []
    for label in labels_set[1:]:
        label_data = data[np.where(labels == label)]
        mean_intensities.append(np.mean(label_data))
    #target_intensity = np.median(mean_intensities)  # GM
    target_intensity = np.max(mean_intensities)  # WM
    #target_intensity = np.min(mean_intensities)  # CSF
    target_label = mean_intensities.index(target_intensity) + 1
    return target_label

def segment(src_path, dst_path, labels_path=None):
    logger.info('Segment on: {}'.format(src_path))
    try:
        data, affine = load_nii(src_path)
        n_clusters = 3

        labels = kmeans_cluster(data, n_clusters)

        target = get_target_label(labels, data)
        gm_mask = np.copy(labels).astype(np.float32)
        gm_mask[np.where(gm_mask != target)] = 0.333
        gm_mask[np.where(gm_mask == target)] = 1.
        data = data.astype(np.float32)
        gm = np.multiply(data, gm_mask)
        save_nii(labels, labels_path, affine)
        save_nii(gm, dst_path, affine)
    except RuntimeError:
        logger.warning('Falid on: {}'.format(src_path))

    return

if __name__ == '__main__':

    # Reference FSL sample template
    refPath = '$FSLDIR/data/standard/MNI152_T1_1mm.nii.gz'

    # Set ART location
    os.environ['ARTHOME'] = '/utils/atra1.0_LinuxCentOS6.7/'

    # Set ACPC Path
    acpc_detect_path='/utils/acpcdetect_v2.1_LinuxCentOS6.7/bin/acpcdetect'

    # ACPC detection

    nii_paths = Path('/data').glob('**/*.nii')
    nii_files = [nii_path for nii_path in nii_paths if nii_path.is_file()]

    for nii_file in nii_files:
        run_acpc_detect(nii_file, acpc_detect_path)


    '''
    # Zip _RAS.nii files.

    niiACPCPaths = Path('/data').glob('**/*_RAS.nii')
    niiACPCFiles = [niiACPCPath for niiACPCPath in niiACPCPaths if niiACPCPath.is_file()]

    for niiFile in niiACPCFiles:
        dstFilePath = niiFile.parent / ('_' + niiFile.name)
        shutil.copyfile(niiFile, dstFilePath)
        subprocess.check_call(['gzip', dstFilePath, '-f'])

    # Run orient2std and registration

    niiGzPaths = Path('/data').glob('**/*.gz')
    niiGzFiles = [niiGzPath for niiGzPath in niiGzPaths if niiGzPath.is_file()]

    regFiles = list()
    for niiGzFile in niiGzFiles:
        niiGzFilePath = niiGzFile.as_posix()
        dstFile = niiGzFile.parent / (niiGzFile.stem.split('.')[0] + '_reg.nii.gz')
        regFiles.append(dstFile)
        dstFilePath = dstFile.as_posix()
        logger.info('Registration on: {}'.format(niiGzFilePath))
        try:
            orient2std(niiGzFilePath, dstFilePath)
            registration(dstFilePath, dstFilePath, refPath)
        except RuntimeError:
            logger.warning('Falied on: {}'.format(niiGzFilePath))

    # Skull stripping

    stripFiles = list()
    for regFile in regFiles:
        regFilePath = regFile.as_posix()
        dstFile = regFile.parent / (regFile.stem.split('.')[0] + '_strip.nii.gz')
        stripFiles.append(dstFile)
        dstFilePath = dstFile.as_posix()
        logger.info('Stripping on : {}'.format(regFilePath))
        try:
            bet(regFilePath, dstFilePath, frac=0.3)
        except RuntimeError:
            logger.warning('Failed on: {}'.format(regFilePath))

    # Bias correction
    bcFiles = list()
    for stripFile in stripFiles:
        stripFilePath = stripFile.as_posix()
        dstFile = stripFile.parent / (stripFile.stem.split('.')[0] + '_bc.nii.gz')
        bcFiles.append(dstFile)
        dstFilePath = dstFile.as_posix()
        bias_field_correction(stripFilePath, dstFilePath)

    # Enhancement
    enhancedFiles = list()
    for bcFile in bcFiles:
        bcFilePath = bcFile.as_posix()
        dstFile = bcFile.parent / (bcFile.stem.split('.')[0] + '_eh.nii.gz')
        enhancedFiles.append(dstFile)
        dstFilePath = dstFile.as_posix()
        enhance(bcFilePath, dstFilePath, kernel_size=3, percentils=[0.5, 99.5], bins_num=256, eh=True)


    # Segmentation
    segmentFiles = list()

    for enhancedFile in enhancedFiles:
        enhancedFilePath = enhancedFile.as_posix()
        dstFile = enhancedFile.parent / (enhancedFile.stem.split('.')[0].split('_')[0] + '_segment.nii.gz')
        labelFile = enhancedFile.parent / (enhancedFile.stem.split('.')[0].split('_')[0] + '_segment_labeled.nii.gz')
        segmentFiles.append(dstFile)
        dstFilePath = dstFile.as_posix()
        labelFilePath = labelFile.as_posix()
        segment(enhancedFilePath, dstFilePath, labels_path=labelFilePath)
    '''


