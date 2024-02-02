from pathlib import Path
import shutil

from nipype import Function
from nipype.pipeline import Node, Workflow

from node.acpc_detect.interface import ACPCDetectInterface
from node.zip.interface import ZipOutputInterface
from node.orient2std.interface import Reorient2StdInterface
from node.registration.interface import FLIRTInterface
from node.skull_stripping.interface import SkullStrippingInterface
from node.bias_field_correction.interface import BiasFieldCorrectionInterface
from node.enhancement.interface import EnhancementInterface
from node.segmentation.interface import SegmentationInterface
from node.draw_segmentation.interface import DrawSegmentationInterface

from utils.convert_dot_to_png import convert_dot_to_png

# ==========================================

# Define the input file and output folder
# List of input NIfTI files to process
input_files = [
    Path('/data/099_S_4205.nii'),
    Path('/data/099_S_4205_2.nii')
]

output_folder = Path('/output')

output_folders = []
for input_file in input_files:
    folder = output_folder / input_file.stem
    folder.mkdir(parents=True, exist_ok=True)
    output_folders.append(folder)
    # Clean the folder
    for file in folder.glob('*'):
        if file.is_file():
            file.unlink()
        if file.is_dir():
            shutil.rmtree(file)

pairs = list(zip(input_files, output_folders))

# ==========================================

# Define the process_pair function
def process_pair(pair):
    input_file, output_folder = pair
    return input_file, output_folder

process_pair_node = Node(
    Function(
        input_names=["pair"],
        output_names=["input_file", "output_folder"],
        function=process_pair
    ),
    name="process_pair"
)
process_pair_node.iterables = [('pair', pairs)]

# Create the acpc node
acpc_node = Node(ACPCDetectInterface(), name='t1_acpc_detect')

# Create the zip node
zip_node = Node(ZipOutputInterface(), name='zip_output')

# Create the orient2std node
orient2std_node = Node(Reorient2StdInterface(), name='orient2std')

# Create the registration node
registration_node = Node(FLIRTInterface(), name='registration')

# Create the skull stripping node
skull_stripping_node = Node(SkullStrippingInterface(), name='skull_stripping')

# Create the bias field correction node
bias_field_correction_node = Node(BiasFieldCorrectionInterface(), name='bias_field_correction')

# Create the enhancement node
enhancement_node = Node(EnhancementInterface(), name='enhancement')

# Create the segmentation node
segmentation_node = Node(SegmentationInterface(), name='segmentation')

# Create the draw segmentation node
draw_gm_segmentation_node = Node(DrawSegmentationInterface(), name='draw_gm_segmentation')
draw_gm_segmentation_node.inputs.title = 'GM@map'
draw_wm_segmentation_node = Node(DrawSegmentationInterface(), name='draw_wm_segmentation')
draw_wm_segmentation_node.inputs.title = 'WM@map'
draw_csf_segmentation_node = Node(DrawSegmentationInterface(), name='draw_csf_segmentation')
draw_csf_segmentation_node.inputs.title = 'CSF@map'

# ==========================================

# Create a workflow
workflow = Workflow(name='preprocess_workflow')
nodes = [
    process_pair_node,
    acpc_node,
    zip_node,
    orient2std_node,
    registration_node, 
    skull_stripping_node,
    bias_field_correction_node,
    enhancement_node,
    segmentation_node,
    draw_gm_segmentation_node,
    draw_wm_segmentation_node,
    draw_csf_segmentation_node,
]
workflow.add_nodes(nodes)

# Connect the input_file_node to the acpc_node (input_file & output_folder)
workflow.connect(process_pair_node, 'input_file', acpc_node, 'input_file')
workflow.connect(process_pair_node, 'output_folder', acpc_node, 'output_folder')

# Connect the acpc_node to the zip_node (input_file & output_folder)
workflow.connect(acpc_node, 'output_file', zip_node, 'input_file')
workflow.connect(process_pair_node, 'output_folder', zip_node, 'output_folder')

# Connect the zip_node to the orient2std_node (input_file & output_folder)
workflow.connect(zip_node, 'output_file', orient2std_node, 'input_file')
workflow.connect(process_pair_node, 'output_folder', orient2std_node, 'output_folder')

# Connect the orient2std_node to the registration_node (input_file & output_folder)
workflow.connect(orient2std_node, 'output_file', registration_node, 'input_file')
workflow.connect(process_pair_node, 'output_folder', registration_node, 'output_folder')

# Connect the registration_node to the skull_stripping_node (input_file & output_folder)
workflow.connect(registration_node, 'output_file', skull_stripping_node, 'input_file')
workflow.connect(process_pair_node, 'output_folder', skull_stripping_node, 'output_folder')

# Connect the skull_stripping_node to the bias_field_correction_node (input_file & output_folder)
workflow.connect(skull_stripping_node, 'output_file', bias_field_correction_node, 'input_file')
workflow.connect(process_pair_node, 'output_folder', bias_field_correction_node, 'output_folder')

# Connect the bias_field_correction_node to the enhancement_node (input_file & output_folder)
workflow.connect(bias_field_correction_node, 'output_file', enhancement_node, 'input_file')
workflow.connect(process_pair_node, 'output_folder', enhancement_node, 'output_folder')

# Connect the enhancement_node to the segmentation_node (input_file & output_folder)
workflow.connect(enhancement_node, 'output_file', segmentation_node, 'input_file')
workflow.connect(process_pair_node, 'output_folder', segmentation_node, 'output_folder')

# Connect acpc_node to draw_gm_segmentation_node (input_file & output_folder)
workflow.connect(acpc_node, 'output_file', draw_gm_segmentation_node, 'acpc_input_file')
workflow.connect(segmentation_node, 'gm_segmented_output_file', draw_gm_segmentation_node, 'segmented_input_file')
workflow.connect(process_pair_node, 'output_folder', draw_gm_segmentation_node, 'output_folder')
# Connect acpc_node to draw_wm_segmentation_node (input_file & output_folder)
workflow.connect(acpc_node, 'output_file', draw_wm_segmentation_node, 'acpc_input_file')
workflow.connect(segmentation_node, 'wm_segmented_output_file', draw_wm_segmentation_node, 'segmented_input_file')
workflow.connect(process_pair_node, 'output_folder', draw_wm_segmentation_node, 'output_folder')
# Connect acpc_node to draw_csf_segmentation_node (input_file & output_folder)
workflow.connect(acpc_node, 'output_file', draw_csf_segmentation_node, 'acpc_input_file')
workflow.connect(segmentation_node, 'csf_segmented_output_file', draw_csf_segmentation_node, 'segmented_input_file')
workflow.connect(process_pair_node, 'output_folder', draw_csf_segmentation_node, 'output_folder')

# ==========================================

# Draw the workflow
workflow.write_graph(graph2use='flat', format='png', simple_form=True)

# Convert the detailed dot file to a png file
convert_dot_to_png('./graph_detailed.dot', './graph_detailed.png')

# Run the workflow
workflow.run()