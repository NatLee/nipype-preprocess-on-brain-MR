from pathlib import Path

from nipype.interfaces.base import SimpleInterface
from nipype.interfaces.base import BaseInterfaceInputSpec
from nipype.interfaces.base import TraitedSpec
from nipype.interfaces.base import File
from nipype.interfaces.base import Directory

from node.acpc_detect.utils import acpc_detect

class ACPCDetectInputSpec(BaseInterfaceInputSpec):
    nii_file = File(exists=True, desc='Path to the NIfTI file', mandatory=True)

class ACPCDetectOutputSpec(TraitedSpec):
    out_file = Directory(desc='Directory with the ACPC detection results')

class ACPCDetectInterface(SimpleInterface):
    input_spec = ACPCDetectInputSpec
    output_spec = ACPCDetectOutputSpec

    def _run_interface(self, runtime):
        nii_file = self.inputs.nii_file
        output_folder = acpc_detect(nii_file)
        out_file = output_folder / (Path(nii_file).stem + '_RAS.nii')
        self._results['out_file'] = out_file.as_posix()
        return runtime

    def _list_outputs(self):
        outputs = self.output_spec().get()
        return outputs