from pathlib import Path

from nipype.interfaces.base import SimpleInterface
from nipype.interfaces.base import BaseInterfaceInputSpec
from nipype.interfaces.base import TraitedSpec
from nipype.interfaces.base import File
from nipype.interfaces.base import Directory

from node.acpc_detect.utils import acpc_detect

from utils.save_nii_as_png import save_nii_as_png

class ACPCDetectInputSpec(BaseInterfaceInputSpec):
    input_file = File(exists=True, desc='Path to the NIfTI file', mandatory=True)
    output_folder = Directory(exists=True, desc='Path to the output folder', mandatory=False)

class ACPCDetectOutputSpec(TraitedSpec):
    output_file = File(exists=True, desc='Directory with the ACPC detection results', mandatory=True)
    output_png_file = File(exists=True, desc='Directory with the ACPC detection PNG image', mandatory=True)

class ACPCDetectInterface(SimpleInterface):
    input_spec = ACPCDetectInputSpec
    output_spec = ACPCDetectOutputSpec

    def _run_interface(self, runtime):
        input_file = Path(self.inputs.input_file)
        output_folder = Path(self.inputs.output_folder)
        new_output_folder = acpc_detect(input_file, output_folder)
        # Only one file is expected
        output_file = new_output_folder / (Path(input_file).stem + '_RAS.nii')
        output_png_file = new_output_folder / (Path(input_file).stem+ '_RAS.png')
        save_nii_as_png(
            output_file,
            output_png_file
        )
        self._results['output_file'] = output_file.as_posix()
        self._results['output_png_file'] = output_png_file.as_posix()
        return runtime

    def _list_outputs(self):
        return self._results