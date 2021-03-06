from ast import literal_eval

import matplotlib.pyplot as plt
import numpy as np
import openslide
import skimage
from shapely.affinity import translate
from shapely.geometry import box

from annotation.model import AnnotationModel, AnnotationGeometry
from annotation_image.core import build_region_data
from annotation_image.reagion_data import RegionData
from common.grid_utils import pos_range
from common.timeit_utils import timing
from common_image.core.img_polygon_utils import create_polygon_image
from common_image.core.resize import resize_ndimg, resize_ndarray
from common_image.model.ndimg import Ndimg
from common_image_qt.core import ndimg_to_qimg
from common_openslide.slide_helper import SlideHelper
from common_shapely.shapely_utils import get_polygon_bbox_size, get_polygon_bbox_pos, scale_at_origin, locate
from filter.common.filter_output import FilterOutput
from filter.common.filter_results import FilterResults
from filter.keras.keras_model_filter_model import KerasModelParams, KerasModelFilterData, \
	KERAS_MODEL_PARAMS_DEFAULT_CMAP, KERAS_MODEL_PARAMS_DEFAULT_COLOR_TUPLE_PATTERN
from slice.annotation_shapely_utils import annotation_geom_to_shapely_geom
from slice.image_shapely_utils import get_slide_polygon_bbox_rgb_region


# @gcached
def load_keras_model(model_path: str):
	from tensorflow.python.keras.saving import load_model
	keras_model = load_model(model_path)
	return keras_model


def keras_model_filter(annotation: AnnotationModel, filter_data: KerasModelFilterData,
					   img_path: str) -> FilterOutput:
	rd = build_region_data(img_path, annotation, annotation.filter_level)
	results = _keras_model_filter(rd, filter_data.keras_model_params)
	return results


# nrows, ncols = get_polygon_bbox_size(polygon0, level_scale)
def convert_image(ndarray: np.ndarray, scale: bool) -> np.ndarray:
	if scale:
		return np.atleast_3d(np.squeeze(ndarray / 255)).astype(np.float32)
	else:
		return np.atleast_3d(ndarray).astype(np.float32)


def convert_patch_label(patch_label):
	classes_count = np.atleast_3d(patch_label).shape[-1]
	if classes_count != 1:
		patch_label = np.argmax(patch_label, axis=-1).astype(dtype=np.float32)
		patch_label = np.expand_dims(patch_label, axis=-1)
		# https://github.com/tensorflow/tensorflow/blob/r1.8/tensorflow/python/keras/_impl/keras/preprocessing/image.py#L313
		patch_label /= classes_count - 1
	return patch_label


# @gcached
@timing
def _keras_model_filter(rd: RegionData, params: KerasModelParams) -> FilterOutput:
	keras_model = load_keras_model(params.model_path)
	input_shape = keras_model.input_shape[1:]
	input_size = input_shape[:2]
	# TODO get from KerasModelParams
	patch_size_scale = params.patch_size_scale or 1
	rescale_source_patch = True
	polygon0 = annotation_geom_to_shapely_geom(
		AnnotationGeometry(annotation_type=rd.annotation_type, origin_point=rd.origin_point, points=rd.points))
	polygon_size0 = get_polygon_bbox_size(polygon0)

	input_size0 = (input_size[0] * patch_size_scale, input_size[1] * patch_size_scale)

	sh = SlideHelper(rd.img_path)
	level = rd.level
	if level is None or level == '':
		level = min(2, sh.level_count - 1)

	level = int(level)
	level_downsample = sh.level_downsamples[level]
	level_scale = 1 / level_downsample
	filter_image_size = get_polygon_bbox_size(polygon0, level_scale)

	# filter_image = np.empty((*filter_image_size, 3), dtype='uint8')
	filter_image = np.zeros((*filter_image_size, 4), dtype='uint8')

	cmap = params.cmap or KERAS_MODEL_PARAMS_DEFAULT_CMAP
	cm = None
	color_tuple = None
	color_arr = None
	color_tuple_indexes = []
	try:
		cm = plt.get_cmap(cmap)
	except ValueError:
		try:
			color_tuple_pattern = literal_eval(cmap)
		except ValueError:
			color_tuple_pattern = KERAS_MODEL_PARAMS_DEFAULT_COLOR_TUPLE_PATTERN
		color_tuple_indexes = [i for i, c in enumerate(color_tuple_pattern) if 'y' == str(c).lower()]
		color_list = [0 if i in color_tuple_indexes else c / 255 for i, c in enumerate(color_tuple_pattern)]
		color_arr = np.array(color_list, dtype=np.float32)

	# height0, width0 = get_polygon_bbox_size(polygon0)
	p0 = get_polygon_bbox_pos(polygon0)
	with openslide.open_slide(rd.img_path) as slide:
		for x0, y0 in pos_range((polygon_size0[1], polygon_size0[0]), input_size0[1], input_size0[0]):
			patch0 = box(x0, y0, x0 + input_size0[1], y0 + input_size0[0])
			patch0 = translate(patch0, p0[0], p0[1])
			patch_image = get_slide_polygon_bbox_rgb_region(slide, patch0, level, rescale_result_image=False)
			patch_image_shape = patch_image.ndarray.shape
			if patch_image_shape[:2] != input_size:
				patch_image = resize_ndimg(patch_image, input_size)
			patch_ndarray = convert_image(patch_image.ndarray, params.scale_image)
			patch_images_batch = np.array([patch_ndarray])
			patch_labels_batch = keras_model.predict(patch_images_batch)
			patch_label = patch_labels_batch[0]
			patch_label = convert_patch_label(patch_label)

			x, y = int(x0 * level_scale), int(y0 * level_scale)
			nrows, ncols = (int(input_size0[0] * level_scale), int(input_size0[1] * level_scale))
			patch_label_ = patch_label
			if patch_label_.shape[:2] != (nrows, ncols):
				patch_label_ = resize_ndarray(patch_label_, (nrows, ncols))
			patch_label_ = skimage.util.invert(patch_label_) if params.invert else patch_label_
			# patch_label_ *= params.alpha_scale

			if cm:
				patch_image = cm(np.squeeze(patch_label_))
			else:
				patch_image = np.zeros((*patch_label_.shape[:2], 4), dtype=np.float32)
				patch_image[:, :, :] = color_arr
				# patch_image[:, :, :3] /= 255
				for i in color_tuple_indexes:
					patch_image[:, :, i] = np.squeeze(patch_label_)
			patch_image[..., 3] *= params.alpha_scale
			patch_image_ubyte = skimage.util.img_as_ubyte(patch_image)
			# patch_image_ubyte = patch_label_.reshape(patch_image_ubyte.shape[:2])
			nrows, ncols = min(nrows, filter_image[y:, ...].shape[0]), min(ncols, filter_image[y:, x:, ...].shape[1])
			filter_image[y:y + nrows, x:x + ncols, ...] = patch_image_ubyte[:nrows, :ncols]

	polygon_ = scale_at_origin(locate(polygon0, polygon0), level_scale)
	bool_mask_ndarray = create_polygon_image(polygon_, 'L', 255, create_mask=False).ndarray
	qimg = ndimg_to_qimg(Ndimg(filter_image, "RGBA", bool_mask_ndarray))
	return FilterOutput(qimg, bool_mask_ndarray, FilterResults(None, None))
