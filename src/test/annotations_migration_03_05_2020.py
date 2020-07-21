import copy

from annotation.annotation_type import AnnotationType
from common import json_utils


def convert_annotation(annotation: dict) -> dict:
    new_annotation = copy.deepcopy(annotation)
    i = annotation['geometry']['annotation_type']
    annotation_type = list(AnnotationType)[i - 1]
    new_annotation['geometry']['annotation_type'] = annotation_type
    if 'stats' in annotation and annotation['stats'] and 'area_text' in annotation['stats']:
        new_annotation['stats']['text'] = annotation['stats']['area_text']
    del new_annotation['text_graphics_view_config']['display_attrs']
    new_annotation['text_graphics_view_config']['display_pattern'] = "{label}\\n{stats[text]}\\n{filter_results[text]}"
    del new_annotation['tree_view_config']['display_attrs']
    new_annotation['tree_view_config']['display_pattern'] = "{label}"
    return new_annotation


def convert_annotations_container(annotations_container: dict) -> dict:
    annotations = annotations_container['annotations']
    new_annotations = {}
    for key, annotation in annotations.items():
        new_annotation = convert_annotation(annotation)
        new_annotations[key] = new_annotation
    new_annotations_container = {'annotations': new_annotations}
    return new_annotations_container


def convert_file(source_path, target_path) -> None:
    annotations_container = json_utils.read(source_path)
    new_annotations_container = convert_annotations_container(annotations_container)
    json_utils.write(target_path, new_annotations_container)


if __name__ == '__main__':
    # convert_file(r'D:\temp\slides\slide1_annotations.json', r'D:\temp\slides\slide1_annotations_new.json')
    # convert_file(r'D:\temp\slides\slide3_annotations.json', r'D:\temp\slides\slide3_annotations_new.json')
    # convert_file(r'D:\temp\slides\slide4_annotations.json', r'D:\temp\slides\slide4_annotations_new.json')
    # convert_file(r'D:\temp\slides\slide5_annotations.json', r'D:\temp\slides\slide5_annotations_new.json')
    # convert_file(r'D:\temp\slides\slide6_annotations.json', r'D:\temp\slides\slide6_annotations_new.json')

    convert_file(r'C:\Users\User\temp\pathadin_examples\data\slide1_annotations.json', r'C:\Users\User\temp\pathadin_examples\data\slide1_annotations.json')
    convert_file(r'C:\Users\User\temp\pathadin_examples\data\slide2_annotations.json', r'C:\Users\User\temp\pathadin_examples\data\slide2_annotations.json')
