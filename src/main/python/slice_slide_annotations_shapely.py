import zipfile
from io import BytesIO
from typing import Dict, Tuple, Iterable

import numpy as np
import openslide
from PIL.Image import Image
from shapely.affinity import translate
from shapely.geometry import Polygon, box, MultiPolygon
from skimage.color import rgba2rgb
from skimage.io import imsave

from grid_utils import pos_to_rect_coords, pos_range
from img.proc.mask import draw_annotation
from shapely_utils import annotation_geom_to_shapely_geom, build_pos_to_annotation_polygons
from slide_viewer.common.file_utils import make_if_not_exists
from slide_viewer.common.slide_helper import SlideHelper
from common_qt.qobjects_convert_util import ftuples_to_ituples
from slide_viewer.ui.model.annotation_type import AnnotationType
from slide_viewer.ui.odict.deep.model import AnnotationModel, AnnotationTreeItems

slide_path = r"D:\slide_cbir_47\temp\slides\slide-2019-09-19T18-08-52-R28-S3.mrxs"
# annotations_path = r"D:\slide_cbir_47\temp\slides\slide-2019-09-19T18-08-52-R28-S3_annotations5.json"
annotations_path = r"D:\slide_cbir_47\temp\slides\slide-2019-09-19T18-08-52-R28-S3_annotations7.json"


def draw_shapely_polygon(img: np.ndarray, color: int, polygon: Polygon):
    ftuples = list(polygon.boundary.coords)
    points = ftuples_to_ituples(ftuples)
    draw_annotation(img, points, AnnotationType.POLYGON, color=color)


def generate_tile_pilimgs(slide_path: str, positions, grid_length: int) -> Iterable[Tuple[Tuple[int, int], Image]]:
    with openslide.open_slide(slide_path) as slide:
        for pos in positions:
            tile_pilimage = slide.read_region((int(pos[0]), int(pos[1])), 0,
                                              (int(grid_length), int(grid_length)))
            yield pos, tile_pilimage


def generate_test_positions(annotations: Dict[str, AnnotationModel], grid_length: int) -> Iterable[Tuple[int, int]]:
    test_annotations = [a for a in annotations.values() if a.label == 'test']
    for annotation in test_annotations:
        geom = annotation_geom_to_shapely_geom(annotation.geometry)
        if geom:
            xmin, ymin, xmax, ymax = geom.bounds
            # geom = translate(geom, -xmin, -ymin)
            size = (xmax - xmin, ymax - ymin)
            for pos in pos_range(size, grid_length, xmin, ymin):
                yield pos
        else:
            # ignore other
            pass


def generate_label_ndimgs(annotations: Dict[str, AnnotationModel], source_size: Tuple[int, int], grid_length: int) \
        -> Iterable[Tuple[Tuple[int, int], np.ndarray]]:
    train_annotations = [a for a in annotations.values() if a.label != 'test']
    pos_to_annotation_polygons = build_pos_to_annotation_polygons(train_annotations, source_size, grid_length)

    # TODO customize filter and sample tiles based on class proportions
    # pos_to_annotation_polygons = {pos: polygons for pos, polygons in pos_to_annotation_polygons.items() if len(polygons) > 1}

    for pos, annotation_polygons in pos_to_annotation_polygons.items():
        # tile_box.coords = [pos, (pos[0] + grid_length, pos[1]), (pos[0] + grid_length, pos[1] + grid_length),
        #                    (pos[0], pos[1] + grid_length), pos]
        tile_box = box(*pos_to_rect_coords(pos, grid_length))
        box_intersections = []
        for annotation_polygon in annotation_polygons:
            box_intersection = tile_box.intersection(annotation_polygon)
            box_intersection = translate(box_intersection, -pos[0], -pos[1])
            box_intersection.annotation_id = annotation_polygon.annotation_id
            box_intersections.append(box_intersection)

        def annotation_polygon_key(annotation_polygon):
            annotation = annotations[annotation_polygon.annotation_id]
            return (annotation.user_attrs.get('label_order', 0), annotation.user_attrs['label_color'])

        box_intersections.sort(key=annotation_polygon_key)
        label_img = np.full((grid_length, grid_length), 0, dtype=np.uint8, order='C')
        for box_intersection in box_intersections:
            annotation = annotations[box_intersection.annotation_id]
            color = annotation.user_attrs['label_color']
            if isinstance(box_intersection, MultiPolygon):
                for polygon in box_intersection:
                    draw_shapely_polygon(label_img, color, polygon)
            else:
                draw_shapely_polygon(label_img, color, box_intersection)
        un = np.unique(label_img)
        # if len(un) == 1:
        #     continue
        yield pos, label_img


# TODO consider origin_point
if __name__ == '__main__':
    annotations_container = AnnotationTreeItems.parse_file(annotations_path)
    annotations = annotations_container.annotations

    slide_helper = SlideHelper(slide_path)
    source_size = slide_helper.level_dimensions[0]
    grid_length = 256

    # import matplotlib.pyplot as plt

    # fig, axs = plt.subplots(nrows=20, ncols=15, figsize=(9, 6), subplot_kw={'xticks': [], 'yticks': []})
    # label_ndimgs = [label_ndimg for pos, label_ndimg in generate_label_ndimgs(annotations, source_size, grid_length)]
    # for plot_cell, label_ndimg in zip(axs.flat, label_ndimgs):
    #     plot_cell.imshow(label_ndimg, cmap='gray', vmin=0, vmax=255)
    # plt.show()

    label_image_dir = f'{grid_length}/train/label/'
    make_if_not_exists(label_image_dir, True)
    pos_list = []
    label_imgs = []
    with zipfile.ZipFile(f'{grid_length}/train_labels_zip.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        for i, (pos, label_image) in enumerate(generate_label_ndimgs(annotations, source_size, grid_length)):
            file_name = f'{label_image_dir}/{i}_{pos}.png'
            buf = BytesIO()
            imsave(buf, label_image, check_contrast=False, format='PNG')
            imsave(file_name, label_image, check_contrast=False, format='PNG')
            imsave(f'{grid_length}/train_labels_zip.zip/{i}_{pos}.png', label_image, check_contrast=False, format='PNG')
            # buf.seek(0)
            zipf.writestr(f'{i}_{pos}.png', buf.getvalue())
            pos_list.append(pos)
            label_imgs.append(label_image)
            print(pos)
    label_imgs_ndarray = np.stack(label_imgs)
    np.savez_compressed(f'{grid_length}/train_labels_ndarray.npz', label_imgs_ndarray)

    image_dir = f'{grid_length}/train/image/'
    make_if_not_exists(image_dir, True)
    ndimgs = []
    with zipfile.ZipFile(f'{grid_length}/train_images_zip_manual.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        for i, (pos, pilimg) in enumerate(generate_tile_pilimgs(slide_path, pos_list, grid_length)):
            file_name = f'{image_dir}/{i}_{pos}.png'
            # pilimg = pilimg.convert("L")
            # pilimg.save(file_name)
            ndimg = rgba2rgb(np.array(pilimg))
            # ndimg = img_as_float(ndimg)
            # ndig = adjust_log(ndimg)
            # ndimg = rgb2hed(ndimg)[..., 0]
            # ndimg = rgb2gray(ndimg)
            imsave(file_name, ndimg, check_contrast=False)
            imsave(f'{grid_length}/train_images_zip_pil.zip/{i}_{pos}.png', ndimg, check_contrast=False, format='PNG', optimize=True)
            buf = BytesIO()
            imsave(buf, ndimg, check_contrast=False, format='PNG')
            zipf.writestr(f'{i}_{pos}.png', buf.getvalue())
            ndimgs.append(ndimg)
    imgs_ndarray = np.stack(ndimgs)
    np.savez_compressed(f'{grid_length}/train_imgs_ndarray.npz', imgs_ndarray)

    # test_image_dir = f'{grid_length}/test/image/'
    # make_if_not_exists(test_image_dir)
    # pos_list = list(generate_test_positions(annotations, grid_length))
    # for i, (pos, pilimg) in enumerate(generate_tile_pilimgs(slide_path, pos_list, grid_length)):
    #     file_name = f'{test_image_dir}/{i}.png'
    #     # pilimg = pilimg.convert("L")
    #     ndimg = np.asarray(pilimg)
    #     ndimg = rgba2rgb(ndimg)
    #     imsave(file_name, ndimg)
    #     # pilimg.save(file_name)
