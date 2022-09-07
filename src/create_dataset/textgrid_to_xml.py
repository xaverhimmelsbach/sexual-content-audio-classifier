import argparse
import os.path

import textgrids
from PIL import Image
from lxml import objectify
from lxml import etree

from src.config import CLASSES


def parse_arguments():
    parser = argparse.ArgumentParser(description="Convert a TextGrid file to XML")
    parser.add_argument("--spectrogram_file", help="Spectrogram file to calculate dimensions from")
    parser.add_argument("--textgrid_file", help="TextGrid file to convert")
    parser.add_argument("--xml_file", help="XML file to write")
    args = parser.parse_args()

    return args.textgrid_file, args.spectrogram_file, args.xml_file


def create_annotation(image_width, image_height, folder, filename):
    # Create root element
    result = objectify.Element("annotation")

    # Create path elements
    folder_element = objectify.SubElement(result, "folder")
    folder_element[0] = folder
    filename_element = objectify.SubElement(result, "filename")
    filename_element[0] = filename
    path_element = objectify.SubElement(result, "path")
    path_element[0] = f"{folder}/{filename}"

    # Create source element
    source_element = objectify.SubElement(result, "source")
    database_element = objectify.SubElement(source_element, "database")
    database_element[0] = "Unknown"

    # Create full image size element
    size_element = objectify.SubElement(result, "size")
    width_element = objectify.SubElement(size_element, "width")
    width_element[0] = str(image_width)
    height_element = objectify.SubElement(size_element, "height")
    height_element[0] = str(image_height)
    depth_element = objectify.SubElement(size_element, "depth")
    depth_element[0] = 3

    # Create segmented element
    segmented_element = objectify.SubElement(result, "segmented")
    segmented_element[0] = "0"

    return result


def create_object(xmin, xmax, image_xmax, image_width, image_height, name):
    # Place a bounding box at full height around each sound
    start_percentage = xmin / image_xmax
    end_percentage = xmax / image_xmax

    start_pixel_x = int(start_percentage * image_width)
    start_pixel_y = 0
    end_pixel_x = int(end_percentage * image_width)
    end_pixel_y = image_height

    # Create object element
    result = objectify.Element("object")

    # Create object description elements
    name_element = objectify.SubElement(result, "name")
    name_element[0] = name
    pose_element = objectify.SubElement(result, "pose")
    pose_element[0] = "Unspecified"
    truncated_element = objectify.SubElement(result, "truncated")
    truncated_element[0] = "0"
    difficult_element = objectify.SubElement(result, "difficult")
    difficult_element[0] = "0"

    # Create bounding box element
    bounding_box_element = objectify.SubElement(result, "bndbox")
    xmin_element = objectify.SubElement(bounding_box_element, "xmin")
    xmin_element[0] = str(start_pixel_x)
    ymin_element = objectify.SubElement(bounding_box_element, "ymin")
    ymin_element[0] = str(start_pixel_y)
    xmax_element = objectify.SubElement(bounding_box_element, "xmax")
    xmax_element[0] = str(end_pixel_x)
    ymax_element = objectify.SubElement(bounding_box_element, "ymax")
    ymax_element[0] = str(end_pixel_y)

    return result


def convert_textgrid_to_xml(textgrid_file, spectrogram_file, xml_file):
    # Load textgrid and spectrogram dimensions
    t = textgrids.TextGrid(textgrid_file)
    im = Image.open(spectrogram_file)
    width, height = im.size

    filename = os.path.basename(spectrogram_file)

    annotation_element = create_annotation(width, height, 'images', filename)

    # Iterate over annotated sound intervals
    for i, sound in enumerate(t.get('sounds')):
        # Skip all intervals that don't contain allowed sounds
        if sound.text not in CLASSES:
            if sound.text != "":
                print(f"Unknown annotation {sound.text} encountered in sound {i}. Skipping...")
            continue

        object_element = create_object(sound.xmin, sound.xmax, t.xmax, width, height, sound.text)
        annotation_element.append(object_element)

    # Remove annotations
    objectify.deannotate(annotation_element, cleanup_namespaces=True)

    # Write out
    with open(xml_file, "w") as f:
        f.write(etree.tostring(annotation_element, pretty_print=True).decode("utf-8"))


if __name__ == "__main__":
    textgrid_file_arg, spectrogram_file_arg, xml_file_arg = parse_arguments()
    convert_textgrid_to_xml(textgrid_file_arg, spectrogram_file_arg, xml_file_arg)
