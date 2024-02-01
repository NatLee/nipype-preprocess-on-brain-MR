from pathlib import Path

import gzip
import shutil

from loguru import logger

from nipype.interfaces.base import SimpleInterface
from nipype.interfaces.base import BaseInterfaceInputSpec
from nipype.interfaces.base import TraitedSpec
from nipype.interfaces.base import File
from nipype.interfaces.base import Directory


class ZipOutputInputSpec(BaseInterfaceInputSpec):
    input_file = File(exists=True, desc='Input file to compress', mandatory=True)
    output_folder = Directory(exists=True, desc='Path to the output folder', mandatory=False)

class ZipOutputOutputSpec(TraitedSpec):
    output_file = File(exists=True, desc='Output compressed file', mandatory=True)

class ZipOutputInterface(SimpleInterface):
    input_spec = ZipOutputInputSpec
    output_spec = ZipOutputOutputSpec

    def _run_interface(self, runtime):
        input_file = self.inputs.input_file
        output_folder = self.inputs.output_folder
        output_zip_folder = Path(output_folder) / 'zip'
        output_file = output_zip_folder / (Path(input_file).name + '.gz')

        logger.info('Compressing {} to {}'.format(input_file, output_file))

        # Create the output directory if it doesn't exist
        output_zip_folder.mkdir(parents=True, exist_ok=True)

        # Clean the folder
        for file in output_zip_folder.glob('*'):
            if file.is_file():
                file.unlink()
            if file.is_dir():
                shutil.rmtree(file)
        
        # Compress the directory
        with open(input_file, 'rb') as f_in, gzip.open(output_file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

        self._results['output_file'] = output_file
        return runtime

    def _list_outputs(self):
        return self._results