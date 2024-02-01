from pathlib import Path
import shutil

from nipype.interfaces.base import (SimpleInterface, BaseInterfaceInputSpec, TraitedSpec, File, traits)
from loguru import logger

from utils.load_nii import load_nii
from utils.save_nii import save_nii

from node.enhancement.utils import denoise
from node.enhancement.utils import rescale_intensity
from node.enhancement.utils import equalize_hist

class EnhancementInputSpec(BaseInterfaceInputSpec):
    input_file = File(exists=True, desc='Source image path (.nii.gz)', mandatory=True)
    output_folder = traits.Directory(exists=False, desc='Output folder for the enhanced image', mandatory=True)
    kernel_size = traits.Int(3, usedefault=True, desc='Kernel size for denoising')
    percentiles = traits.List([0.5, 99.5], usedefault=True, desc='Percentiles for intensity rescaling')
    bins_num = traits.Int(256, usedefault=True, desc='Number of bins for histogram equalization')
    eh = traits.Bool(True, usedefault=True, desc='Enable histogram equalization')

class EnhancementOutputSpec(TraitedSpec):
    output_file = File(exists=True, desc='Path to the enhanced image')

class EnhancementInterface(SimpleInterface):
    input_spec = EnhancementInputSpec
    output_spec = EnhancementOutputSpec

    def _run_interface(self, runtime):
        input_file = self.inputs.input_file
        output_folder = Path(self.inputs.output_folder)
        output_enhancement_folder = output_folder / 'enhancement'
        
        kernel_size = self.inputs.kernel_size
        percentiles = self.inputs.percentiles
        bins_num = self.inputs.bins_num
        eh = self.inputs.eh
        enhanced_image_path = output_enhancement_folder / Path(input_file.name)

        logger.info(f'Preprocess on: {input_file}')
        logger.info(f'Output: {enhanced_image_path}')

        # Ensure the output directory exists
        output_enhancement_folder.mkdir(parents=True, exist_ok=True)

        # Clean up the output directory
        for file in output_enhancement_folder.glob('*'):
            if file.is_file():
                file.unlink()
            if file.is_dir():
                shutil.rmtree(file)

        try:
            # Load the image and perform enhancement
            volume, affine = load_nii(input_file)
            volume = denoise(volume, kernel_size)
            volume = rescale_intensity(volume, percentiles, bins_num)
            if eh:
                volume = equalize_hist(volume, bins_num)

            save_nii(volume, str(enhanced_image_path), affine)
            self._results['output_file'] = str(enhanced_image_path)

        except RuntimeError as e:
            logger.warning(f'Failed on: {input_file} with error: {e}')

        return runtime

    def _list_outputs(self):
        return self._results
