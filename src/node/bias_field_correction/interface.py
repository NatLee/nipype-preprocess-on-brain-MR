import shutil
from pathlib import Path

from loguru import logger
from nipype.interfaces.base import (SimpleInterface, BaseInterfaceInputSpec, TraitedSpec, File, Directory)
from nipype.interfaces.ants import N4BiasFieldCorrection

class BiasFieldCorrectionInputSpec(BaseInterfaceInputSpec):
    input_file = File(exists=True, desc='Source image path (.nii.gz)', mandatory=True)
    output_folder = Directory(exists=False, desc='Output folder for the bias corrected image', mandatory=True)

class BiasFieldCorrectionOutputSpec(TraitedSpec):
    output_file = File(exists=True, desc='Path to the bias corrected image')

class BiasFieldCorrectionInterface(SimpleInterface):
    input_spec = BiasFieldCorrectionInputSpec
    output_spec = BiasFieldCorrectionOutputSpec

    def _run_interface(self, runtime):
        input_file = self.inputs.input_file
        output_folder = Path(self.inputs.output_folder)
        output_bias_correction_folder = output_folder / 'bias_correction'
        output_file = output_bias_correction_folder / Path(input_file).name

        logger.info(f'N4ITK on: {input_file}')
        logger.info(f'Output: {output_file}')

        # Ensure the output directory exists
        output_bias_correction_folder.mkdir(parents=True, exist_ok=True)

        # Clean up the output directory
        for file in output_bias_correction_folder.glob('*'):
            if file.is_file():
                file.unlink()
            if file.is_dir():
                shutil.rmtree(file)

        try:
            n4 = N4BiasFieldCorrection()
            n4.inputs.input_image = str(input_file)
            n4.inputs.output_image = str(output_file)
            n4.inputs.dimension = 3
            n4.inputs.n_iterations = [100, 100, 60, 40]
            n4.inputs.shrink_factor = 3
            n4.inputs.convergence_threshold = 1e-4
            n4.inputs.bspline_fitting_distance = 300
            n4.run()

            self._results['output_file'] = str(output_file)

        except RuntimeError as e:
            logger.warning(f'Failed on: {input_file} with error: {e}')

        return runtime

    def _list_outputs(self):
        return self._results
