import shutil
from pathlib import Path

from loguru import logger

from nipype.interfaces.base import SimpleInterface, BaseInterfaceInputSpec, TraitedSpec, File, Directory
from nipype.interfaces.fsl import Reorient2Std

class Reorient2StdInputSpec(BaseInterfaceInputSpec):
    input_file = File(exists=True, desc='Input file to reorient', mandatory=True)
    output_folder = Directory(exists=False, desc='Path to the output folder', mandatory=True)

class Reorient2StdOutputSpec(TraitedSpec):
    output_file = File(exists=True, desc='Reoriented output file')

class Reorient2StdInterface(SimpleInterface):
    input_spec = Reorient2StdInputSpec
    output_spec = Reorient2StdOutputSpec

    def _run_interface(self, runtime):
        input_file = self.inputs.input_file
        output_folder = Path(self.inputs.output_folder)
        output_orient_folder = output_folder / 'orient2std'
        output_file = output_orient_folder / Path(input_file).name

        logger.info(f'Reorienting {input_file} to standard space')
        logger.info(f'Output file: {output_file}')

        # Ensure the output directory exists
        output_orient_folder.mkdir(parents=True, exist_ok=True)

        # Clean the folder
        for file in output_orient_folder.glob('*'):
            if file.is_file():
                file.unlink()
            if file.is_dir():
                shutil.rmtree(file)

        # Perform the reorientation
        reorient = Reorient2Std(in_file=input_file, out_file=str(output_file))
        reorient.run()

        self._results['output_file'] = str(output_file)

        return runtime

    def _list_outputs(self):
        super(Reorient2StdInterface, self)._list_outputs()
        return self._results
