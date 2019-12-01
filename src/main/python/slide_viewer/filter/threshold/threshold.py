import cv2
import numpy as np
from PIL import Image

from slide_viewer.filter.threshold.skimage_threshold import skimage_threshold
from slide_viewer.ui.common.img.img_mode_convert import convert_filter_results
from slide_viewer.ui.common.img.img_object_convert import expose_pilimage_buffer_to_ndarray
from slide_viewer.ui.model.filter.base_filter import FilterResults
from slide_viewer.ui.model.filter.threshold_filter import ThresholdFilterData, SkimageAutoThresholdFilterData, \
    ManualThresholdFilterData, HSVManualThresholdFilterData, GrayManualThresholdFilterData
from slide_viewer.ui.slide.widget.histogram_builder import build_histogram_html_for_ndimg


def process_threshold_filter(fr: FilterResults, filter_data: ThresholdFilterData) -> FilterResults:
    if isinstance(filter_data, SkimageAutoThresholdFilterData):
        # img = convert_pilimage(img, 'L')
        fr = convert_filter_results(fr, 'L')
        if isinstance(fr.img, Image.Image):
            img = expose_pilimage_buffer_to_ndarray(fr.img)
        elif isinstance(fr.img, np.ndarray):
            img = fr.img
        else:
            raise ValueError(f"Unsupported img type for process_threshold_filter: {fr.img}")
        threshold = skimage_threshold(img, filter_data)
        threshold_range = (int(threshold), 255)
    elif isinstance(filter_data, ManualThresholdFilterData):
        if isinstance(filter_data, HSVManualThresholdFilterData):
            threshold_range = filter_data.hsv_range
        elif isinstance(filter_data, GrayManualThresholdFilterData):
            threshold_range = filter_data.gray_range
        else:
            raise ValueError(f"Unsupported filter threshold type: {filter_data.threshold_type}")
        # img = convert_pilimage(img, filter_data.color_mode.name)
        fr = convert_filter_results(fr, filter_data.color_mode.name)
        if isinstance(fr.img, Image.Image):
            img = expose_pilimage_buffer_to_ndarray(fr.img)
        elif isinstance(fr.img, np.ndarray):
            img = fr.img
        else:
            raise ValueError(f"Unsupported img type for process_threshold_filter: {fr.img}")
    else:
        raise ValueError(f"Unsupported filter: {filter_data}")
        # threshold_range = None

    if threshold_range is not None:
        lower, upper = threshold_range
        lower, upper = np.array(lower), np.array(upper)
        # TODO inplace?
        # TODO what if lower differs from source_img in channels? 3-tuple lower and 4-tuple rgba?
        # cv2.threshold(self.source_img, lower, upper, cv2.THRESH_BINARY, self.result_img)
        img_arr = img
        result_img = cv2.inRange(img_arr, lower, upper)
        # cv2.inRange(self.source_img, lower, upper, self.result_img)
        fr.img = result_img
        fr.color_mode = 'L'
        histogram_html = build_histogram_html_for_ndimg(fr.img)
        fr.metadata['normed_hist'] = histogram_html
        return fr
        # return expose_ndarray_buffer_to_pillowimage(result_img, "L")
