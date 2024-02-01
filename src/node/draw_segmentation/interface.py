import shutil
from pathlib import Path

from nipype.interfaces.base import (SimpleInterface, BaseInterfaceInputSpec, TraitedSpec, File, Directory)
from loguru import logger

from utils.draw_segmentation import draw_segmentation

class DrawSegmentationInputSpec(BaseInterfaceInputSpec):
    acpc_input_file = File(exists=True, desc='ACPC aligned Source image path (.nii.gz)', mandatory=True)
    segmented_input_file = File(exists=True, desc='Segmented Source image path (.nii.gz)', mandatory=True)
    output_folder = Directory(exists=False, desc='Output folder for the segmented image', mandatory=True)

class DrawSegmentationOutputSpec(TraitedSpec):
    output_file = File(exists=True, desc='Path to png image')

class DrawSegmentationInterface(SimpleInterface):
    input_spec = DrawSegmentationInputSpec
    output_spec = DrawSegmentationOutputSpec

    def _run_interface(self, runtime):
        acpc_input_file = self.inputs.acpc_input_file
        segmented_input_file = self.inputs.segmented_input_file

        output_folder = Path(self.inputs.output_folder)
        output_draw_folder = output_folder / 'draw_segmentation'
        output_draw_sub_folder = output_draw_folder / Path(segmented_input_file).stem

        # Specify the output png path
        output_png_path = output_draw_sub_folder / 'segmented.png'

        logger.info(f'Running draw segmentation for {segmented_input_file} to {output_png_path}')

        # Ensure the output directory exists
        output_draw_sub_folder.mkdir(parents=True, exist_ok=True)

        # Clean up the output directory
        for file in output_draw_sub_folder.glob('*'):
            if file.is_file():
                file.unlink()
            if file.is_dir():
                shutil.rmtree(file)

        draw_segmentation(
            input_nii_path=acpc_input_file,
            input_seg_nii_path=segmented_input_file,
            output_png_path=output_png_path.absolute().as_posix()
        )

        return runtime

    def _list_outputs(self):
        return self._results
