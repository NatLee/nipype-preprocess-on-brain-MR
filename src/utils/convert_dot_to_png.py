import pydot

from loguru import logger

def convert_dot_to_png(dot_file_path, png_file_path):
    """
    Reads a DOT file and saves it as a PNG file.

    Args:
    dot_file_path (str): The path to the DOT file.
    png_file_path (str): The path to save the PNG file.
    """
    # Load the dot file
    graphs = pydot.graph_from_dot_file(dot_file_path)

    # In case there are multiple graphs, iterate over each
    for graph in graphs:
        graph.write_png(png_file_path)

    logger.info(f"Saved PNG file to {png_file_path}")
