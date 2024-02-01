import shutil
from pathlib import Path

from nipype.interfaces.base import (SimpleInterface, BaseInterfaceInputSpec, TraitedSpec, File, Directory)
from loguru import logger

from utils.load_nii import load_nii
from utils.save_nii import save_nii

from node.segmentation.utils import kmeans_cluster
from node.segmentation.utils import get_target_labels
from node.segmentation.utils import segment

class SegmentationInputSpec(BaseInterfaceInputSpec):
    input_file = File(exists=True, desc='Source image path (.nii.gz)', mandatory=True)
    output_folder = Directory(exists=False, desc='Output folder for the segmented image', mandatory=True)

class SegmentationOutputSpec(TraitedSpec):
    gm_segmented_output_file = File(exists=True, desc='Path to GM segmented image')
    wm_segmented_output_file = File(exists=True, desc='Path to WM segmented image')
    csf_segmented_output_file = File(exists=True, desc='Path to CSF segmented image')

    gm_labels_output_file = File(exists=True, desc='Path to GM labels image')
    wm_labels_output_file = File(exists=True, desc='Path to WM labels image')
    csf_labels_output_file = File(exists=True, desc='Path to CSF labels image')

class SegmentationInterface(SimpleInterface):
    input_spec = SegmentationInputSpec
    output_spec = SegmentationOutputSpec

    def _run_interface(self, runtime):
        input_file = self.inputs.input_file
        output_folder = Path(self.inputs.output_folder)
        output_segmentation_folder = output_folder / 'segmentation'

        # Specify the labels and segmented image paths
        gm_labels_path = output_segmentation_folder / (Path(input_file).stem + '_gm_labels.nii.gz')
        wm_labels_path = output_segmentation_folder / (Path(input_file).stem + '_wm_labels.nii.gz')
        csf_labels_path = output_segmentation_folder / (Path(input_file).stem + '_csf_labels.nii.gz')

        gm_segmented_image_path = output_segmentation_folder / (Path(input_file).stem + '_gm_segmented.nii.gz')
        wm_segmented_image_path = output_segmentation_folder / (Path(input_file).stem + '_wm_segmented.nii.gz')
        csf_segmented_image_path = output_segmentation_folder / (Path(input_file).stem + '_csf_segmented.nii.gz')

        logger.info(f'Segment on: {input_file}')
        logger.info(f'Output folder: {output_segmentation_folder}')

        # Ensure the output directory exists
        output_segmentation_folder.mkdir(parents=True, exist_ok=True)

        # Clean up the output directory
        for file in output_segmentation_folder.glob('*'):
            if file.is_file():
                file.unlink()
            if file.is_dir():
                shutil.rmtree(file)

        try:
            # Load the image data and perform K-means clustering
            data, affine = load_nii(input_file)
            
            # Split the data into 3 clusters (GM, WM, CSF)
            n_clusters = 3

            labels = kmeans_cluster(data, n_clusters)

            gm_target, wm_target, csf_target = get_target_labels(labels, data)

            g_matter = segment(labels, data, gm_target)
            save_nii(labels, str(gm_labels_path), affine)
            save_nii(g_matter, str(gm_segmented_image_path), affine)

            w_matter = segment(labels, data, wm_target)
            save_nii(labels, str(wm_labels_path), affine)
            save_nii(w_matter, str(wm_segmented_image_path), affine)

            c_matter = segment(labels, data, csf_target)
            save_nii(labels, str(csf_labels_path), affine)
            save_nii(c_matter, str(csf_segmented_image_path), affine)

            self._results['gm_segmented_output_file'] = str(gm_segmented_image_path)
            self._results['gm_labels_output_file'] = str(gm_labels_path)
            self._results['wm_segmented_output_file'] = str(wm_segmented_image_path)
            self._results['wm_labels_output_file'] = str(wm_labels_path)
            self._results['csf_segmented_output_file'] = str(csf_segmented_image_path)
            self._results['csf_labels_output_file'] = str(csf_labels_path)

        except RuntimeError as e:
            logger.warning(f'Failed on: {input_file} with error: {e}')

        return runtime

    def _list_outputs(self):
        return self._results
