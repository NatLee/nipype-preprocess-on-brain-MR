import os
import shutil
from pathlib import Path

from nipype.interfaces.base import (SimpleInterface, BaseInterfaceInputSpec, TraitedSpec, File, Directory)
from nipype.interfaces.fsl import FLIRT

from loguru import logger

REF_NII_TEMPLATE = os.getenv('FSLDIR') + '/data/standard/MNI152_T1_1mm.nii.gz'

class FLIRTInputSpec(BaseInterfaceInputSpec):
    input_file = File(exists=True, desc='Source image path (.nii.gz)', mandatory=True)
    ref_file = File(exists=True, desc='Reference image path', mandatory=False)
    output_folder = Directory(exists=False, desc='Output folder for the registered image', mandatory=True)

class FLIRTOutputSpec(TraitedSpec):
    out_file = File(exists=True, desc='Path to the registered image')

class FLIRTInterface(SimpleInterface):
    input_spec = FLIRTInputSpec
    output_spec = FLIRTOutputSpec

    def _run_interface(self, runtime):
        input_file = self.inputs.input_file
        output_folder = Path(self.inputs.output_folder)
        output_reg_folder = output_folder / 'registration'
        out_file = output_reg_folder / Path(input_file).name

        # Use the default FSL reference image if ref_file is not provided
        ref_file = self.inputs.ref_file
        if not ref_file:
            ref_file = REF_NII_TEMPLATE

        logger.info('Registering {} to {}'.format(input_file, ref_file))
        logger.info('Reference file: {}'.format(ref_file))
        logger.info('Output file: {}'.format(out_file))

        # Ensure the output directory exists
        output_reg_folder.mkdir(parents=True, exist_ok=True)

        # Clean up the output directory
        for file in output_reg_folder.glob('*'):
            if file.is_file():
                file.unlink()
            if file.is_dir():
                shutil.rmtree(file)

        # Setup FLIRT interface
        flirt = FLIRT(
            in_file=input_file,
            reference=Path(ref_file).as_posix(),
            out_file=str(out_file),
            bins=256,
            cost_func='corratio',
            searchr_x=[0, 0],
            searchr_y=[0, 0],
            searchr_z=[0, 0],
            dof=12,
            interp='spline'
        )
        
        # Execute FLIRT
        flirt.run()

        self._results['out_file'] = str(out_file)

        return runtime

    def _list_outputs(self):
        return self._results
