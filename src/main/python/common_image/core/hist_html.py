import numpy as np

from common_image.core.hist import HistResults


def build_histogram_html_(hist_results: HistResults) -> str:
    return build_histogram_html(hist_results.sorted_most_freq_colors, hist_results.sorted_most_freq_colors_counts)


def build_histogram_html(sorted_most_freq_colors: np.ndarray, sorted_most_freq_colors_counts_normed: np.ndarray) -> str:
    max_points = 7
    bars = []
    color_fraction_ = list(zip(sorted_most_freq_colors, sorted_most_freq_colors_counts_normed))
    for color, fraction in color_fraction_[:max_points]:
        npoints = '.' * int(fraction * max_points)
        if isinstance(color, np.ndarray) and np.squeeze(color).size == 1:
            color = np.squeeze(color)
            color_rgba = (color, color, color, 255)
        elif isinstance(color, np.ndarray) and len(color.shape) == 3:
            color_rgba = (*tuple(color), 255)
        elif isinstance(color, np.ndarray):
            color_rgba = tuple(color)
        else:
            color_rgba = (color, color, color, 255)
        inverse_color_rgba = (255 - color_rgba[0], 255 - color_rgba[1], 255 - color_rgba[2], 255)
        fraction_percent = int(fraction * 100)
        bar_html = f'<div style="background-color: rgba{color_rgba}; color: rgba{inverse_color_rgba}">{fraction_percent}%{npoints}</div>'
        bars.append(bar_html)
    if len(sorted_most_freq_colors) > max_points:
        other_color = np.average(sorted_most_freq_colors[max_points:])
        color_rgba = (other_color, other_color, other_color, 255)
        inverse_color_rgba = (255 - color_rgba[0], 255 - color_rgba[1], 255 - color_rgba[2], 255)
        fraction = np.sum(sorted_most_freq_colors_counts_normed[max_points:])
        fraction_percent = int(fraction * 100)
        bar_html = f'<div style="background-color: rgba{color_rgba}; color: rgba{inverse_color_rgba}">{fraction_percent}% - other...</div>'
        bars.append(bar_html)

    histogram_html = '<div>' + ''.join(bars) + '</div>'
    return histogram_html
