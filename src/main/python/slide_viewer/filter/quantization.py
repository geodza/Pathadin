from PIL import Image
from dataclasses import asdict

from slide_viewer.common.dict_utils import remove_none_values, narrow_dict
from slide_viewer.ui.model.filter.quantization_filter import QuantizationFilterData, QuantizationFilterData_


def process_quantization_filter(img: Image.Image, filter_data: QuantizationFilterData) -> Image.Image:
    kwargs = remove_none_values(narrow_dict(asdict(filter_data),
                                            [QuantizationFilterData_.colors, QuantizationFilterData_.method]))
    quantized = img.quantize(**kwargs)
    quantized = quantized.convert(img.mode)
    return quantized