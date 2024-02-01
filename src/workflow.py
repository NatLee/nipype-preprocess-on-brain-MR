from pathlib import Path
import shutil

from nipype.pipeline import Node, Workflow
from nipype.interfaces.utility import IdentityInterface

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
input_file = Path('/data/099_S_4205.nii')
output_folder = Path('/data/099_S_4205')

# Clean up the output folder if it already exists
if output_folder.exists():
    shutil.rmtree(output_folder)
output_folder.mkdir(parents=True, exist_ok=True)
output_folder.chmod(0o777)

# Define input node with 'input_file' as its input field
input_file_node = Node(IdentityInterface(fields=['input_file']), name='inputspec')
input_file_node.inputs.input_file = input_file

# Create the acpc node
acpc_node = Node(ACPCDetectInterface(), name='t1_acpc_detect')
acpc_node.inputs.output_folder = output_folder

# Create the zip node
zip_node = Node(ZipOutputInterface(), name='zip_output')
zip_node.inputs.output_folder = output_folder

# Create the orient2std node
orient2std_node = Node(Reorient2StdInterface(), name='orient2std')
orient2std_node.inputs.output_folder = output_folder

# Create the registration node
registration_node = Node(FLIRTInterface(), name='registration')
registration_node.inputs.output_folder = output_folder

# Create the skull stripping node
skull_stripping_node = Node(SkullStrippingInterface(), name='skull_stripping')
skull_stripping_node.inputs.output_folder = output_folder

# Create the bias field correction node
bias_field_correction_node = Node(BiasFieldCorrectionInterface(), name='bias_field_correction')
bias_field_correction_node.inputs.output_folder = output_folder

# Create the enhancement node
enhancement_node = Node(EnhancementInterface(), name='enhancement')
enhancement_node.inputs.output_folder = output_folder

# Create the segmentation node
segmentation_node = Node(SegmentationInterface(), name='segmentation')
segmentation_node.inputs.output_folder = output_folder

# Create the draw segmentation node
draw_gm_segmentation_node = Node(DrawSegmentationInterface(), name='draw_gm_segmentation')
draw_gm_segmentation_node.inputs.output_folder = output_folder
draw_gm_segmentation_node.inputs.title = 'GM Prob. map'
draw_wm_segmentation_node = Node(DrawSegmentationInterface(), name='draw_wm_segmentation')
draw_wm_segmentation_node.inputs.output_folder = output_folder
draw_wm_segmentation_node.inputs.title = 'WM Prob. map'
draw_csf_segmentation_node = Node(DrawSegmentationInterface(), name='draw_csf_segmentation')
draw_csf_segmentation_node.inputs.output_folder = output_folder
draw_csf_segmentation_node.inputs.title = 'CSF Prob. map'

# ==========================================

# Create a workflow
workflow = Workflow(name='preprocess_workflow')
nodes = [
    input_file_node,
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

# Connect the input_file_node to the acpc_node
workflow.connect(input_file_node, 'input_file', acpc_node, 'input_file')

# Connect the acpc_node to the zip_node
workflow.connect(acpc_node, 'output_file', zip_node, 'input_file')

# Connect the zip_node to the orient2std_node
workflow.connect(zip_node, 'output_file', orient2std_node, 'input_file')

# Connect the orient2std_node to the registration_node
workflow.connect(orient2std_node, 'output_file', registration_node, 'input_file')

# Connect the registration_node to the skull_stripping_node
workflow.connect(registration_node, 'output_file', skull_stripping_node, 'input_file')

# Connect the skull_stripping_node to the bias_field_correction_node
workflow.connect(skull_stripping_node, 'output_file', bias_field_correction_node, 'input_file')

# Connect the bias_field_correction_node to the enhancement_node
workflow.connect(bias_field_correction_node, 'output_file', enhancement_node, 'input_file')

# Connect the enhancement_node to the segmentation_node
workflow.connect(enhancement_node, 'output_file', segmentation_node, 'input_file')


# Connect acpc_node to draw_gm_segmentation_node
workflow.connect(acpc_node, 'output_file', draw_gm_segmentation_node, 'acpc_input_file')
workflow.connect(segmentation_node, 'gm_segmented_output_file', draw_gm_segmentation_node, 'segmented_input_file')
# Connect acpc_node to draw_wm_segmentation_node
workflow.connect(acpc_node, 'output_file', draw_wm_segmentation_node, 'acpc_input_file')
workflow.connect(segmentation_node, 'wm_segmented_output_file', draw_wm_segmentation_node, 'segmented_input_file')
# Connect acpc_node to draw_csf_segmentation_node
workflow.connect(acpc_node, 'output_file', draw_csf_segmentation_node, 'acpc_input_file')
workflow.connect(segmentation_node, 'csf_segmented_output_file', draw_csf_segmentation_node, 'segmented_input_file')


# ==========================================

# Draw the workflow
workflow.write_graph(graph2use='flat', format='png', simple_form=True)

# Convert the detailed dot file to a png file
convert_dot_to_png('./graph_detailed.dot', './graph_detailed.png')

# Run the workflow
workflow.run()