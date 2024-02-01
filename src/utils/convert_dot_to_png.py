import pydot

from loguru import logger

def convert_dot_to_png(dot_file_path, png_file_path):
    """
    Reads a DOT file and saves it as a PNG file.

    Args:
    dot_file_path (str): The path to the DOT file.
    png_file_path (str): The path to save the PNG file.
    """
    # Load the dot file from string
    with open(dot_file_path) as f:
        dot_file_contents = f.read()
        dot_file_contents = dot_file_contents.replace('\n', '') # avoid blank rectangle in the png file

    (graph,) = pydot.graph_from_dot_data(dot_file_contents)

    # Save the dot file as a PNG file
    graph.write_png(png_file_path)

    logger.info(f"Saved PNG file to {png_file_path}")
