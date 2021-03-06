from collections import OrderedDict
from typing import Tuple, Dict
import numpy as np

from common.timeit_utils import timing
from common_image.core.hist import HistResults


def build_histogram_html_(hist_results: HistResults) -> str:
	return build_histogram_html(hist_results.sorted_most_freq_colors, hist_results.sorted_most_freq_colors_counts)


def color_to_rgba(color) -> Tuple[int, int, int, int]:
	if isinstance(color, np.ndarray) and color.ravel().size == 1:
		color = color.ravel()[0]
		color_rgba = (color, color, color, 255)
	elif isinstance(color, np.ndarray) and color.ravel().size == 3:
		color_rgba = (*tuple(color.ravel()), 255)
	elif isinstance(color, np.ndarray):
		color_rgba = tuple(color.ravel())
	else:
		color_rgba = (color, color, color, 255)
	return color_rgba


def color_to_rgb(color) -> Tuple[int, int, int]:
	if isinstance(color, np.ndarray) and color.ravel().size == 1:
		color = color.ravel()[0]
		color_rgb = (color, color, color)
	elif isinstance(color, np.ndarray) and color.ravel().size == 3:
		color_rgb = tuple(color.ravel())
	elif isinstance(color, np.ndarray):
		color_rgb = tuple(color.ravel())
	else:
		color_rgb = (color, color, color)
	return color_rgb


@timing
def build_histogram_html(sorted_most_freq_colors: np.ndarray, sorted_most_freq_colors_counts_normed: np.ndarray,
						 max_points=7) -> str:
	bars = []
	color_fraction_ = list(zip(sorted_most_freq_colors, sorted_most_freq_colors_counts_normed))
	for color, fraction in color_fraction_[:max_points]:
		npoints = '.' * int(fraction * max_points)
		color_rgba = color_to_rgba(color)
		inverse_color_rgba = (255 - color_rgba[0], 255 - color_rgba[1], 255 - color_rgba[2], 255)
		fraction_percent = int(fraction * 100)
		bar_html = f'<div style="background-color: rgba{color_rgba}; color: rgba{inverse_color_rgba}">&nbsp;{fraction_percent}%{npoints}</div>'
		bars.append(bar_html)
	if len(sorted_most_freq_colors) > max_points:
		other_color = np.average(sorted_most_freq_colors[max_points:])
		color_rgba = color_to_rgba(other_color)
		inverse_color_rgba = (255 - color_rgba[0], 255 - color_rgba[1], 255 - color_rgba[2], 255)
		fraction = np.sum(sorted_most_freq_colors_counts_normed[max_points:])
		fraction_percent = int(fraction * 100)
		bar_html = f'<div style="background-color: rgba{color_rgba}; color: rgba{inverse_color_rgba}">&nbsp;{fraction_percent}% - other...</div>'
		bars.append(bar_html)

	histogram_html = '<div>' + ''.join(bars) + '</div>'
	return histogram_html


def color_rgba_to_hex(color_rgba) -> str:
	return "#{:02X}{:02X}{:02X}{:02X}".format(*color_rgba)


def color_rgb_to_hex(color_rgb) -> str:
	return "#{:02X}{:02X}{:02X}".format(*color_rgb)


def build_hist_dict(sorted_most_freq_colors: np.ndarray, sorted_most_freq_colors_counts_normed: np.ndarray,
					max_points=None) -> Dict[str, float]:
	color_fraction_ = list(zip(sorted_most_freq_colors, sorted_most_freq_colors_counts_normed))
	if max_points is not None:
		color_fraction_ = color_fraction_[:max_points]
	color_hex_to_fraction = OrderedDict()
	for color, fraction in color_fraction_:
		color_rgb = color_to_rgb(color)
		color_hex = color_rgb_to_hex(color_rgb)
		color_hex_to_fraction[color_hex] = fraction
	return color_hex_to_fraction


def build_hist_dict2(sorted_most_freq_colors: np.ndarray, sorted_most_freq_colors_counts_normed: np.ndarray,
					 max_points=None) -> Dict[Tuple, float]:
	color_fraction_ = list(zip(sorted_most_freq_colors, sorted_most_freq_colors_counts_normed))
	if max_points is not None:
		color_fraction_ = color_fraction_[:max_points]
	color_rgba_to_fraction = OrderedDict()
	for color, fraction in color_fraction_:
		color_rgba = color_to_rgba(color)
		color_rgba_to_fraction[color_rgba] = fraction
	return color_rgba_to_fraction
