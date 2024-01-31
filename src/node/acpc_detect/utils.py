from pathlib import Path

import tempfile
import shutil
import subprocess
import os
from loguru import logger


# Set ART location
os.environ['ARTHOME'] = '/utils/atra1.0_LinuxCentOS6.7/'

# ACPC detection executable path
ACPC_DETECT_BIN_PATH = '/utils/acpcdetect_v2.1_LinuxCentOS6.7/bin/acpcdetect'


def acpc_detect(nii_file: str) -> Path:
    logger.info('ACPC detection on: {}'.format(nii_file))

    # Convert `nii_file` to a Path object
    nii_file_path = Path(nii_file)
    # Specify the output folder
    output_folder = nii_file_path.parent / nii_file_path.stem / 'acpc'

    # Use a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)

        # Copy the .nii file to the temporary directory
        temp_nii_file_path = temp_dir_path / nii_file_path.name
        shutil.copy(nii_file_path, temp_nii_file_path)

        # Modify the command to use the new .nii file path in the temporary directory
        command = [ACPC_DETECT_BIN_PATH, "-no-tilt-correction", "-center-AC", "-nopng", "-noppm", "-i", str(temp_nii_file_path)]

        # Run the command
        subprocess.call(command, stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)

        # Create a folder as the same name as the .nii file
        Path(output_folder).mkdir(parents=True, exist_ok=True)

        # Clean the folder
        for file in output_folder.glob('*'):
            if file.is_file():
                file.unlink()
            if file.is_dir():
                shutil.rmtree(file)

        # Move the output files to the folder
        for file in temp_dir_path.glob('*'):
            #logger.info('Moving {} to {}'.format(file, output_folder))
            shutil.move(file, output_folder)

        # Use Path to change mode of the folder (include all files)
        (output_folder.parent).chmod(0o777)

    return output_folder
