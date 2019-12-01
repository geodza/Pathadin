from dataclasses import replace

from slide_viewer.ui.common.common import get_default_arg
from slide_viewer.ui.common.editor.range.range_util import is_valid_range, default_range
from slide_viewer.ui.model.color_mode import is_valid_color_mode, default_color_mode
from slide_viewer.ui.model.filter.quantization_filter import PillowQuantizeMethod, QuantizationFilterData, \
    QuantizationFilterData_
from slide_viewer.ui.model.filter.threshold_filter import ThresholdFilterData, ThresholdFilterData_, \
    ManualThresholdFilterData, SkimageAutoThresholdFilterData, SkimageAutoThresholdFilterData_, \
    SkimageMeanThresholdFilterData, SkimageMinimumThresholdFilterData, SkimageMinimumThresholdFilterData_, \
    ThresholdType, SkimageThresholdType
from slide_viewer.ui.model.filter.base_filter import FilterData, FilterData_, FilterType


def dict_to_filterdata(dict_: dict) -> FilterData:
    if dict_[FilterData_.filter_type] == FilterType.THRESHOLD:
        return dict_to_thresholdfilterdata(dict_)
    elif dict_[FilterData_.filter_type] == FilterType.QUANTIZATION:
        return dict_to_data_ignore_extra(dict_, QuantizationFilterData)


def dict_to_thresholdfilterdata(dict_: dict) -> ThresholdFilterData:
    if dict_[ThresholdFilterData_.threshold_type] == ThresholdType.MANUAL:
        return dict_to_data_ignore_extra(dict_, ManualThresholdFilterData)
    elif dict_[ThresholdFilterData_.threshold_type] == ThresholdType.SKIMAGE_AUTO:
        return dict_to_skimagethresholdfilterdata(dict_)


def dict_to_skimagethresholdfilterdata(dict_: dict) -> SkimageAutoThresholdFilterData:
    if dict_[SkimageAutoThresholdFilterData_.skimage_threshold_type] == SkimageThresholdType.threshold_mean:
        return dict_to_data_ignore_extra(dict_, SkimageMeanThresholdFilterData)
    elif dict_[SkimageAutoThresholdFilterData_.skimage_threshold_type] == SkimageThresholdType.threshold_minimum:
        return dict_to_data_ignore_extra(dict_, SkimageMinimumThresholdFilterData)


def is_valid_manualthresholdfilterdata(fd: ManualThresholdFilterData):
    return is_valid_color_mode(fd.color_mode) and is_valid_range(fd.threshold_range, fd.color_mode)


def is_valid_nbins(nbins):
    return isinstance(nbins, int) and nbins > 0


def is_valid_max_iter(max_iter):
    return isinstance(max_iter, int) and max_iter > 0


def is_valid_colors(colors):
    return isinstance(colors, int) and colors > 0


def is_valid_pillow_quantize_method(pillow_quantize_method):
    return isinstance(pillow_quantize_method, PillowQuantizeMethod) or pillow_quantize_method is None


def is_valid_quantizationfilterdata(fd: QuantizationFilterData):
    return is_valid_colors(fd.colors) and is_valid_pillow_quantize_method(fd.method)


def is_valid_skimageminimumthresholdfilterdata(fd: SkimageMinimumThresholdFilterData):
    return is_valid_nbins(fd.nbins) and is_valid_max_iter(fd.max_iter)


def is_valid_skimageautothresholdfilterdata(fd: SkimageAutoThresholdFilterData):
    if fd.skimage_threshold_type == SkimageThresholdType.threshold_mean:
        return True
    elif fd.skimage_threshold_type == SkimageThresholdType.threshold_minimum:
        return is_valid_skimageminimumthresholdfilterdata(fd)
    return True


def is_valid_thresholdfilterdata(fd: ThresholdFilterData):
    if fd.threshold_type == ThresholdType.MANUAL:
        return is_valid_manualthresholdfilterdata(fd)
    elif fd.threshold_type == ThresholdType.SKIMAGE_AUTO:
        return is_valid_skimageautothresholdfilterdata(fd)


def is_valid_filterdata(fd: FilterData):
    if fd.filter_type == FilterType.THRESHOLD:
        return is_valid_thresholdfilterdata(fd)
    elif fd.filter_type == FilterType.QUANTIZATION:
        return is_valid_quantizationfilterdata(fd)


def create_valid_quantizationfilterdata(fd: QuantizationFilterData):
    if not is_valid_colors(fd.colors):
        fd = replace(fd, **{QuantizationFilterData_.colors: QuantizationFilterData.colors})
    if not is_valid_pillow_quantize_method(fd.method):
        fd = replace(fd, **{QuantizationFilterData_.method: QuantizationFilterData.method})
    return fd


def create_valid_thresholdfilterdata(fd: ThresholdFilterData):
    if fd.threshold_type == ThresholdType.MANUAL:
        return create_valid_manualthresholdfilterdata(fd)
    elif fd.threshold_type == ThresholdType.SKIMAGE_AUTO:
        return create_valid_skimageautothresholdfilterdata(fd)


def create_valid_manualthresholdfilterdata(fd: ManualThresholdFilterData):
    if not is_valid_color_mode(fd.color_mode):
        fd = replace(fd, color_mode=default_color_mode())
    if not is_valid_range(fd.threshold_range, fd.color_mode):
        fd = replace(fd, threshold_range=default_range(fd.color_mode))
    return fd


def create_valid_skimageminimumthresholdfilterdata(fd: SkimageMinimumThresholdFilterData):
    if not is_valid_nbins(fd.nbins):
        from skimage.filters import threshold_minimum
        fd = replace(fd, nbins=get_default_arg(threshold_minimum, SkimageMinimumThresholdFilterData_.nbins))
    if not is_valid_max_iter(fd.max_iter):
        fd = replace(fd, max_iter=get_default_arg(threshold_minimum, SkimageMinimumThresholdFilterData_.max_iter))
    return fd


def create_valid_skimageautothresholdfilterdata(fd: SkimageAutoThresholdFilterData):
    if fd.skimage_threshold_type == SkimageThresholdType.threshold_mean:
        return fd
    elif fd.skimage_threshold_type == SkimageThresholdType.threshold_minimum:
        return create_valid_skimageminimumthresholdfilterdata(fd)


def create_valid_filterdata(fd: FilterData):
    if fd.filter_type == FilterType.THRESHOLD:
        return create_valid_thresholdfilterdata(fd)
    elif fd.filter_type == FilterType.QUANTIZATION:
        return create_valid_quantizationfilterdata(fd)