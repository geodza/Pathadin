import pathlib
import shutil
from collections import defaultdict
from itertools import islice
from math import ceil
from typing import List, Tuple, Iterable, Callable

import cv2
import h5py
import numpy as np
import openslide
from matplotlib import pyplot as plt
from shapely.geometry import Polygon, box
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union
from shapely.prepared import prep
from shapely.strtree import STRtree
from skimage import io
from skimage.io import imshow

from common.grid_utils import pos_range
from img.filter.base_filter import FilterData, FilterType
from img.filter.kmeans_filter import KMeansFilterData
from img.filter.skimage_threshold import SkimageThresholdParams, SkimageThresholdType
from img.ndimagedata import NdImageData
from img.proc.convert import pilimg_to_ndimg
from img.proc.img_mode_convert import convert_ndimg2
from img.proc.threshold.skimage_threshold import ndimg_to_skimage_threshold_range
from img.proc.threshold.threshold import ndimg_to_thresholded_ndimg
from shapely_utils import annotation_to_geom, locate, scale_at_origin, get_polygon_bbox_size, get_polygon_bbox_pos, create_probably_contains_func
from common.file_utils import remove_if_exists
from slide_viewer.ui.odict.deep.model import AnnotationTreeItems, AnnotationModel

slide_path = r"D:\slide_cbir_47\temp\slides\slide-2019-09-19T18-08-52-R28-S3.mrxs"
# annotations_path = r"D:\slide_cbir_47\temp\slides\slide-2019-09-19T18-08-52-R28-S3_annotations5.json"
annotations_path = r"D:\slide_cbir_47\temp\slides\slide-2019-09-19T18-08-52-R28-S3_annotations7_1.json"

# slide_path = r'C:\Users\User\GoogleDisk\Pictures\mosaic1.jpg'

nchannels_to_empty_color = {1: (0,), 3: (0, 255, 0), 4: (0, 0, 0, 255)}
color_mode_to_empty_color = {'L': (0,), 'RGB': (0, 255, 0), 'RGBA': (0, 0, 0, 255)}


def imgshow(img, title='123', **kwargs):
    # return
    plt.title(title)
    imshow(img, **kwargs)
    plt.show()


def create_empty_image(nrows: int, ncols: int, color_mode: str) -> NdImageData:
    # return np.empty((nrows, ncols, nchannels), dtype=np.uint8)
    nchannels = len(color_mode)
    ndimg_ = np.zeros((nrows, ncols, nchannels), dtype=np.uint8)
    # ndimg_ = np.tile(np.array(color_mode_to_empty_color[color_mode], dtype=np.uint8), (nrows, ncols, 1))
    return NdImageData(ndimg_, color_mode, None)


def create_image_for_polygon(polygon: Polygon, color_mode: str, color=None, create_mask=True) -> NdImageData:
    nrows, ncols = get_polygon_bbox_size(polygon)
    img = create_empty_image(nrows, ncols, color_mode)
    if color is not None:
        points = polygon.boundary.coords
        points = np.array(points, dtype=np.int32).reshape((1, -1, 2), order='C')
        cv2.fillPoly(img.ndimg, points, color)
    if create_mask:
        img_boolean_mask = create_image_for_polygon(polygon, 'L', 255, create_mask=False).ndimg
    else:
        img_boolean_mask = None
    return NdImageData(img.ndimg, color_mode, img_boolean_mask)


def imgresize(ndimg: NdImageData, nrows_ncols: Tuple[int, int]) -> NdImageData:
    print(f"resize: {ndimg.ndimg.shape}->{nrows_ncols}")
    ndimg_ = cv2.resize(ndimg.ndimg, nrows_ncols[::-1])
    ndimg_ = np.atleast_3d(ndimg_)
    mask_ = cv2.resize(ndimg.bool_mask_ndimg, nrows_ncols[::-1], interpolation=cv2.INTER_NEAREST) if ndimg.bool_mask_ndimg is not None else None
    mask_ = np.atleast_3d(mask_) if mask_ is not None else None
    return NdImageData(ndimg_, ndimg.color_mode, mask_)


def get_polygon_bbox_image_view(img: np.ndarray, polygon: Polygon) -> np.ndarray:
    # minx, miny, maxx, maxy = tuple(int(b) for b in polygon.bounds)
    x, y = get_polygon_bbox_pos(polygon)
    nrows, ncols = get_polygon_bbox_size(polygon)
    polygon_ndimg = img[y:y + nrows, x:x + ncols]
    return polygon_ndimg


def draw_source_on_target(target: NdImageData, target_mask_polygon: Polygon, source: NdImageData) -> None:
    target_region = get_polygon_bbox_image_view(target.ndimg, target_mask_polygon)
    source_ = imgresize(source, target_region.shape[:2])
    source_ = convert_ndimg2(source_, target.color_mode)
    # imgshow(source_.ndimg, 'prepared source image')
    # imgshow(target_region, 'Target(canvas)')
    # TODO target may have mask too, combine it with source_ mask through AND?
    cv2.subtract(target_region, target_region, target_region, mask=source_.bool_mask_ndimg)
    # imgshow(target_region, 'Target(canvas) after substract')
    cv2.add(source_.ndimg, target_region, target_region, mask=source_.bool_mask_ndimg)
    # imgshow(target_region, 'Target(canvas) result')
    # imgshow(target.ndimg, 'Target(canvas) resulting img')
    pass


def get_slide_polygon_bbox_rgb_region(slide: openslide.AbstractSlide, polygon: Polygon, level: int) -> NdImageData:
    """
    :param polygon: polygon with 0level coordinates
    :return: polygon bbox slide region downsized by level scale with color mode 'RGBA'
    """
    pos = get_polygon_bbox_pos(polygon)
    level_scale = 1 / slide.level_downsamples[level]
    nrows, ncols = get_polygon_bbox_size(polygon, level_scale)
    pilimg = slide.read_region(pos, level, (ncols, nrows))
    pilimg = pilimg.convert('RGB')
    # TODO consider borders, mirroring if region intersects border of slide
    ndimg = pilimg_to_ndimg(pilimg)
    return ndimg


def get_filter(id: str) -> FilterData:
    return None


def process_filter(img: NdImageData, filter_data: FilterData) -> NdImageData:
    converted_ndimgdata = convert_ndimg2(img, 'L')
    params = SkimageThresholdParams(SkimageThresholdType.threshold_mean, {})
    threshold_range = ndimg_to_skimage_threshold_range(params, converted_ndimgdata)
    return ndimg_to_thresholded_ndimg(threshold_range, converted_ndimgdata)


def create_annotation_polygon_image(slide: openslide.AbstractSlide,
                                    annotation: AnnotationModel, annotation_geom: Polygon, polygon: Polygon,
                                    zlayers_rtrees: List[STRtree]) -> NdImageData:
    # filter = get_filter(annotation.filter_id)
    # filter_level = annotation.filter_level
    filter = KMeansFilterData("123")
    filter_level = 2
    level_scale = 1 / slide.level_downsamples[filter_level]

    # TODO mask color - is filter too!?
    mask_color = annotation.user_attrs.get('label_color')
    if mask_color is not None:
        polygon_ = scale_at_origin(locate(polygon, polygon), level_scale)
        return create_image_for_polygon(polygon_, 'L', mask_color)

    if filter.filter_type in [FilterType.KMEANS]:
        source_polygon = annotation_geom
    else:
        source_polygon = polygon
    target_polygon = scale_at_origin(locate(polygon, source_polygon), level_scale)

    source = create_layer_polygon_image(slide, source_polygon, filter_level, zlayers_rtrees[:-1])
    target_ = process_filter(source, filter)
    target = get_polygon_bbox_image_view(target_.ndimg, target_polygon)
    return NdImageData(target, target_.color_mode, target_.bool_mask_ndimg)


def create_layer_polygon_image(slide: openslide.AbstractSlide, polygon: Polygon, level: int,
                               zlayers_rtrees: List[STRtree]) -> NdImageData:
    if not zlayers_rtrees:
        return get_slide_polygon_bbox_rgb_region(slide, polygon, level)

    # We search intersections only for last(top most) z-index layer.
    # We do not search intersections for all layers to detect if polygon is fully labeled or is inside ROI.
    # It means all filtering of not relevant patches must be performed outside.
    probable_intersecting_geoms = zlayers_rtrees[-1].query(polygon)
    intersecting_geoms = [geom for geom in probable_intersecting_geoms if geom.intersects(polygon)]
    intersecting_geoms_intersections = [geom.intersection(polygon) for geom in intersecting_geoms]
    intersection_area = sum([i.area for i in intersecting_geoms_intersections])

    level_scale = 1 / slide.level_downsamples[level]
    if intersection_area != polygon.area:
        below_layer_polygon_img = create_layer_polygon_image(slide, polygon, level, zlayers_rtrees[:-1])
        polygon_img = below_layer_polygon_img
    else:
        polygon_ = scale_at_origin(polygon, level_scale)
        polygon_img = create_image_for_polygon(polygon_, 'RGB')

    for intersecting_geom, intersecting_geom_intersection in zip(intersecting_geoms, intersecting_geoms_intersections):
        if not isinstance(intersecting_geom_intersection, Polygon):
            # TODO consider geometry collection containing polygon
            print(f"Ignoring not Polygon intersection ${intersecting_geom_intersection}")
            continue
        intersecting_geom_intersection_ = scale_at_origin(locate(intersecting_geom_intersection, polygon), level_scale)
        annotation_polygon_image = create_annotation_polygon_image(slide, intersecting_geom.annotation, intersecting_geom,
                                                                   intersecting_geom_intersection_, zlayers_rtrees[:-1])
        draw_source_on_target(polygon_img, intersecting_geom_intersection_, annotation_polygon_image)

    return polygon_img


def generate_patches(slide_path: str, level: int, grid_length: int, stride: int = None, x_offset: int = 0, y_offset: int = 0,
                     annotations_path=None,
                     patch_pos_filter_hook: Callable[[Tuple[int, int]], bool] = None,
                     patch_intersections_filter_hook: Callable[[Polygon, List[BaseGeometry], List[Tuple[BaseGeometry, BaseGeometry]]], bool] = None) \
        -> Iterable[Tuple[Tuple[int, int], NdImageData]]:
    # TODO replace with template method pattern
    stride = stride or grid_length

    if annotations_path:
        annotations_container = AnnotationTreeItems.parse_file(annotations_path)
        annotations = annotations_container.annotations

        train_annotations = [a for a in annotations.values() if a.label != 'test']

        annotation_geoms = [annotation_to_geom(a, True) for a in train_annotations]
        z_to_geoms = defaultdict(list)
        for geom in annotation_geoms:
            z = geom.annotation.user_attrs.get('z_index', 0)
            z_to_geoms[z].append(geom)

        z_list = sorted(z_to_geoms.keys())
        rtree = STRtree(annotation_geoms)
        zlayers_rtrees = list([STRtree(z_to_geoms[z]) for z in z_list])

        # (minx, miny), (maxx, maxy) = annotations['45'].geometry.points
        # grid_length = max(maxx - minx, maxy - miny) + 1

        roi_annotations = [a for a in annotations.values() if a.user_attrs.get('roi')]
        roi_annotations_geoms = [annotation_to_geom(a, True) for a in roi_annotations]
        if roi_annotations_geoms:
            roi_annotations_geoms_union = unary_union(roi_annotations_geoms)
            roi_annotations_geoms_union_probably_contains = create_probably_contains_func(*roi_annotations_geoms_union.bounds)
            roi_annotations_geoms_union = prep(roi_annotations_geoms_union)
        else:
            roi_annotations_geoms_union = None
            roi_annotations_geoms_union_probably_contains = None
    else:
        zlayers_rtrees = []
        roi_annotations_geoms_union = None
        roi_annotations_geoms_union_probably_contains = None
        rtree = None
        annotation_geoms = []

    with openslide.open_slide(slide_path) as slide:
        source_size = slide.level_dimensions[0]
        # TODO patch_generator as param
        for x, y in pos_range(source_size, stride, x_offset, y_offset):
            if patch_pos_filter_hook:
                if not patch_intersections_filter_hook((x, y)):
                    continue
            if roi_annotations_geoms_union:
                if not roi_annotations_geoms_union_probably_contains(x, y, x + grid_length, y + grid_length):
                    continue
                patch = box(x, y, x + grid_length, y + grid_length)
                if not roi_annotations_geoms_union.contains(patch):
                    continue
            if patch_intersections_filter_hook:
                probable_intersecting_geoms = rtree.query(patch)
                intersecting_geoms = [g for g in probable_intersecting_geoms if g.intersects(patch)]
                intersecting_geoms_intersections = [g.intersection(patch) for g in intersecting_geoms]
                if not patch_intersections_filter_hook(patch, annotation_geoms, list(zip(intersecting_geoms, intersecting_geoms_intersections))):
                    continue

            img = create_layer_polygon_image(slide, patch, level, zlayers_rtrees)
            # TODO hook? if we do not like result image (if its fully white or fully black, we may throw it away and continue)
            yield ((x, y), img)


def generate_patches2(slide_path: str, pos_generator, level: int, grid_length, x_offset: int = 0, y_offset: int = 0,
                      annotations_path=None) \
        -> Iterable[Tuple[Tuple[int, int], NdImageData]]:
    # TODO replace with template method pattern
    if annotations_path:
        annotations_container = AnnotationTreeItems.parse_file(annotations_path)
        annotations = annotations_container.annotations
        train_annotations = [a for a in annotations.values() if a.label != 'test']
        annotation_geoms = [annotation_to_geom(a, True) for a in train_annotations]
        z_to_geoms = defaultdict(list)
        for geom in annotation_geoms:
            z = geom.annotation.user_attrs.get('z_index', 0)
            z_to_geoms[z].append(geom)

        z_list = sorted(z_to_geoms.keys())
        zlayers_rtrees = list([STRtree(z_to_geoms[z]) for z in z_list])
    else:
        zlayers_rtrees = []
    with openslide.open_slide(slide_path) as slide:
        # TODO patch_generator as param
        # TODO consider offset
        for (x, y) in pos_generator:
            patch = box(x, y, x + grid_length, y + grid_length)
            img = create_layer_polygon_image(slide, patch, level, zlayers_rtrees)
            # TODO hook? if we do not like result image (if its fully white or fully black, we may throw it away and continue)
            yield ((x, y), img)


def pos_tee(patches_generator: Iterable[Tuple[Tuple[int, int], NdImageData]], pos_collector: List[Tuple[int, int]]):
    for ((x, y), img) in patches_generator:
        pos_collector.append((x, y))
        yield ((x, y), img)


def collect_image_labels_to_npz(label_patches_generator: Iterable[Tuple[Tuple[int, int], NdImageData]],
                                slide_path: str, level: int, grid_length,
                                root_folder: str, npz_image_file_name: str,
                                npz_label_file_name: str,
                                patch_file_name_format: str = '{patch_num}_({x},{y})'):
    pos_collector = []
    label_patches_generator = pos_tee(label_patches_generator, pos_collector)
    collect_patches_to_npz(label_patches_generator, root_folder, npz_label_file_name, patch_file_name_format)
    img_patches_generator = generate_patches2(slide_path, pos_collector, level, grid_length)
    collect_patches_to_npz(img_patches_generator, root_folder, npz_image_file_name, patch_file_name_format)


def collect_patches_to_dict(patches_generator: Iterable[Tuple[Tuple[int, int], NdImageData]],
                            patch_key_format: str = '{patch_num}_({x},{y})'):
    imgs = {}
    for patch_num, ((x, y), img) in enumerate(patches_generator):
        patch_key = patch_key_format.format(patch_num=patch_num, x=x, y=y)
        imgs[patch_key] = img.ndimg
    return imgs


def collect_patches_to_npz(patches_generator: Iterable[Tuple[Tuple[int, int], NdImageData]],
                           root_folder: str, npz_file_name: str, patch_file_name_format: str = '{patch_num}_({x},{y})',
                           *, delete_working_folder=False) -> None:
    # TODO replace with template method pattern
    from os.path import join as pjoin
    # We add predefined_working_folder to path to avoid accidental deleting of folder specified by user
    predefined_working_folder = 'patches'
    working_folder = pjoin(root_folder, predefined_working_folder)
    if delete_working_folder:
        shutil.rmtree(working_folder, True)
    pathlib.Path(working_folder).mkdir(parents=True, exist_ok=True)
    imgs = collect_patches_to_dict(patches_generator, patch_file_name_format)
    # ext=pathlib.Path(patch_file_name).suffix or '.npz'
    npz_file_path = pjoin(working_folder, npz_file_name)
    remove_if_exists(npz_file_path)
    np.savez_compressed(npz_file_path, **imgs)


def collect_patches_to_folder(patches_generator: Iterable[Tuple[Tuple[int, int], NdImageData]],
                              root_folder: str, patch_file_name_format: str = 'data.zip/{patch_num}_({x},{y}).png',
                              *, delete_working_folder=False) -> None:
    # TODO replace with template method pattern
    from os.path import join as pjoin
    # We add predefined_working_folder to path to avoid accidental deleting of folder specified by user
    predefined_working_folder = 'patches'
    working_folder = pjoin(root_folder, predefined_working_folder)
    if delete_working_folder:
        shutil.rmtree(working_folder, True)
    pathlib.Path(working_folder).mkdir(parents=True, exist_ok=True)
    for patch_num, ((x, y), img) in enumerate(patches_generator):
        patch_file_name = patch_file_name_format.format(patch_num=patch_num, x=x, y=y)
        patch_file_path = pjoin(working_folder, patch_file_name)
        io.imsave(patch_file_path, img.ndimg, check_contrast=False)


def collect_patches_to_npy(patches_generator: Iterable[Tuple[Tuple[int, int], NdImageData]],
                           root_folder: str, npy_file_name: str,
                           *, delete_working_folder=False) -> None:
    # TODO replace with template method pattern
    from os.path import join as pjoin
    # We add predefined_working_folder to path to avoid accidental deleting of folder specified by user
    predefined_working_folder = 'patches'
    working_folder = pjoin(root_folder, predefined_working_folder)
    if delete_working_folder:
        shutil.rmtree(working_folder, True)
    pathlib.Path(working_folder).mkdir(parents=True, exist_ok=True)
    imgs = []
    for patch_num, ((x, y), img) in enumerate(patches_generator):
        imgs.append(img.ndimg)
    # ext=pathlib.Path(patch_file_name).suffix or '.npz'
    npy_file_path = pjoin(working_folder, npy_file_name)
    imgs_arr = np.vstack(imgs)
    remove_if_exists(npy_file_path)
    np.save(npy_file_path, imgs_arr)


def npz_imgshow(file_path: str, slice_from, slice_to=None):
    npzfile = np.load(file_path)
    file_names = npzfile.files[slice_from: slice_to]
    arrs = [npzfile[file_name] for file_name in file_names]
    # imgshow(np.vstack(arrs))
    cols = 10
    rows = ceil(len(arrs) / cols)
    for i, arr in enumerate(arrs):
        ax = plt.subplot(rows, cols, i + 1)
        ax.axis('off')
        plt.imshow(arr)
    plt.show()


def collect_patches_to_h5py(patches_generator: Iterable[Tuple[Tuple[int, int], NdImageData]],
                            root_folder: str,
                            h5py_filename: str,
                            dataset_name: str,
                            patch_key_format: str = '{patch_num}_({x},{y})',
                            # dataset_name_format: str = '{patch_num}_({x},{y})',
                            compression="gzip",
                            *, delete_file=False) -> None:
    # TODO replace with template method pattern
    from os.path import join as pjoin
    # We add predefined_working_folder to path to avoid accidental deleting of folder specified by user
    predefined_working_folder = 'patches'
    working_folder = pjoin(root_folder, predefined_working_folder)
    pathlib.Path(working_folder).mkdir(parents=True, exist_ok=True)
    h5py_filepath = pjoin(working_folder, h5py_filename)
    imgs = collect_patches_to_dict(patches_generator, patch_key_format)
    # with h5py.File(h5py_filepath, 'w' if delete_file else 'a') as file:
    #     for dataset_name, img in imgs.items():
    #         if dataset_name in file:
    #             del file[dataset_name]
    #         file.create_dataset(dataset_name, data=img, compression=compression)
    img_arr = np.stack(list(imgs.values()))
    with h5py.File(h5py_filepath, 'w' if delete_file else 'a') as file:
        if dataset_name in file:
            del file[dataset_name]
        file.create_dataset(dataset_name, data=img_arr, compression=compression)
        file[dataset_name].attrs['keys'] = list(imgs.keys())


if __name__ == '__main__':
    # npz_imgshow('256/patches/image.npz', 0, 100)
    # npz_imgshow('256/patches/label.npz', 0, 100)
    # TODO consider image and mask slide shifts
    # TODO consider (level, grid_length, stride) collection?
    # TODO consider imbalanced data
    # TODO consider different objective-powers of slides? Do rescale to some target objective-power?
    # TODO consider color mode conversion hooks (at least at start we dont need RGBA)
    shapes = set()
    imgs = []
    level = 0
    grid_length = 256
    stride = grid_length // 1
    patches_generator = generate_patches(slide_path, level, grid_length, stride, 0, 0, annotations_path)
    patches_generator = islice(patches_generator, 100)

    slide_name = pathlib.Path(slide_path).name
    collect_patches_to_h5py(patches_generator, f'{grid_length}', '1000.h5', f'{slide_name}')

    # collect_patches_to_folder(islice(patches_generator, 100), f'{grid_length}', delete_working_folder=True)
    # collect_patches_to_npz(islice(patches_generator, 10000), f'{grid_length}', 'data', delete_working_folder=False)
    # collect_patches_to_npy(islice(patches_generator, 100), f'{grid_length}', 'data', delete_working_folder=False)

    # collect_image_labels_to_npz(patches_generator, slide_path, level, grid_length, f'{grid_length}',
    #                             'image', 'label')

    # for (x, y), ndimgdata in generate_patches(slide_path, level, grid_length, stride, 0, 0, annotations_path):
    #     img = ndimgdata.ndimg
    #     if not img.shape in shapes:
    #         shapes.add(img.shape)
    #         print(img.shape)
    #     imgshow(img, 'Result patch img')
    #     imgs.append(img)
    # gimg[y:y + grid_length, x: x + grid_length, :] = img
    # print(f"total images:{len(imgs)}")
    # ncols = ceil(len(imgs) ** 0.5)
    # nrows = ceil(len(imgs) / ncols)
    # imgs_required_len = nrows * ncols
    # if imgs_required_len > len(imgs):
    #     missing_imgs_len = imgs_required_len - len(imgs)
    #     imgs.extend([create_empty_image(imgs[0].shape[0], imgs[0].shape[1], 'RGBA').ndimg for i in range(missing_imgs_len)])
    # sublists = ((row * ncols, row * ncols + ncols) for row in range(nrows))
    # sublists = list(sublists)
    # sizes = set(s[1] - s[0] for s in sublists)
    # gimg = np.vstack([np.hstack(imgs[sublist[0]:sublist[1]]) for sublist in sublists])
    # gimg = gimg.reshape((-1, ncols * imgs[0].shape[0], gimg.shape[-1]))
    # imsave('img1.png', gimg)
