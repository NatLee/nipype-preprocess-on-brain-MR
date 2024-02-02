import shutil
from pathlib import Path

from nipype.interfaces.base import (SimpleInterface, BaseInterfaceInputSpec, TraitedSpec, File, Directory, traits)

from loguru import logger

class FinalOutputInputSpec(BaseInterfaceInputSpec):
    acpc_output_file = File(exists=True, desc="ACPC corrected NIfTI file (.nii)", mandatory=True)
    acpc_output_png_file = File(exists=True, desc="ACPC corrected PNG file", mandatory=True)
    gm_png_file = File(exists=True, desc="Gray matter segmentation PNG file", mandatory=True)
    wm_png_file = File(exists=True, desc="White matter segmentation PNG file", mandatory=True)
    csf_png_file = File(exists=True, desc="CSF segmentation PNG file", mandatory=True)
    output_folder = Directory(desc="Final output directory", mandatory=True)

class FinalOutputOutputSpec(TraitedSpec):
    output_folder = Directory(exists=True, desc="Directory containing organized final outputs")

class OrganizeFinalOutputInterface(SimpleInterface):
    input_spec = FinalOutputInputSpec
    output_spec = FinalOutputOutputSpec

    def _run_interface(self, runtime):
        # Ensure the output directory exists
        output_dir = Path(self.inputs.output_folder) / "final_output"
        output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Organizing final output in {output_dir}")

        # Clean the output directory
        for file in output_dir.glob("*"):
            if file.is_file():
                file.unlink()
            if file.is_dir():
                shutil.rmtree(file)

        # Copy or move the ACPC output and PNG files to the output directory
        shutil.copy(self.inputs.acpc_output_file, output_dir / Path(self.inputs.acpc_output_file).name)
        shutil.copy(self.inputs.acpc_output_png_file, output_dir / Path(self.inputs.acpc_output_png_file).name)
        shutil.copy(self.inputs.gm_png_file, output_dir / "GM_Segmentation.png")
        shutil.copy(self.inputs.wm_png_file, output_dir / "WM_Segmentation.png")
        shutil.copy(self.inputs.csf_png_file, output_dir / "CSF_Segmentation.png")

        self._results['output_folder'] = str(output_dir)
        return runtime

    def _list_outputs(self):
        return self._results