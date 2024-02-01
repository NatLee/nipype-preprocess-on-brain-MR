import shutil
from pathlib import Path

from nipype.interfaces.base import (SimpleInterface, BaseInterfaceInputSpec, TraitedSpec, File, traits)
from nipype.interfaces.fsl import BET

class SkullStrippingInputSpec(BaseInterfaceInputSpec):
    input_file = File(exists=True, desc='Source image path (.nii.gz)', mandatory=True)
    output_folder = traits.Directory(exists=False, desc='Output folder for the extracted brain image', mandatory=True)
    frac = traits.Float(default_value=0.5, usedefault=True, desc='Fractional intensity threshold', mandatory=False)

class SkullStrippingOutputSpec(TraitedSpec):
    output_file = File(exists=True, desc='Path to the extracted brain image')

class SkullStrippingInterface(SimpleInterface):
    input_spec = SkullStrippingInputSpec
    output_spec = SkullStrippingOutputSpec

    def _run_interface(self, runtime):
        input_file = self.inputs.input_file

        output_folder = Path(self.inputs.output_folder)
        output_skull_stripping_folder = output_folder / 'skull_stripping'
        output_file = output_skull_stripping_folder / Path(input_file).name

        frac = self.inputs.frac

        # Ensure the output directory exists
        output_skull_stripping_folder.mkdir(parents=True, exist_ok=True)

        # Clean up the output directory
        for file in output_skull_stripping_folder.glob('*'):
            if file.is_file():
                file.unlink()
            if file.is_dir():
                shutil.rmtree(file)

        bet = BET(in_file=input_file, out_file=output_file, frac=frac, robust=True)
        res = bet.run()

        self._results['output_file'] = res.outputs.out_file # here get BET's output named `out_file`

        return runtime

    def _list_outputs(self):
        return self._results
