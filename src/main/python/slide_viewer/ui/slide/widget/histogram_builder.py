import numpy as np


def build_histogram_html_for_ndimg(ndimg: np.ndarray) -> str:
    if ndimg.ndim == 3:
        color_arrays = ndimg.reshape(-1, ndimg.shape[-1])
    else:
        color_arrays = ndimg.reshape(-1)
    unique_colors, unique_counts = np.unique(color_arrays, return_counts=True, axis=0)
    # k = 5 if len(unique_counts) > 5 else 0
    k = len(unique_counts)
    # print(f"k: {k} unique_counts: {unique_counts}")
    most_freq_colors_indices = np.argpartition(unique_counts, len(unique_counts) - k - 1)[-k:]
    sorted_most_freq_colors_indices = most_freq_colors_indices[np.argsort(unique_counts[most_freq_colors_indices])]
    sorted_most_freq_colors_indices = sorted_most_freq_colors_indices[::-1]
    sorted_most_freq_colors = unique_colors[sorted_most_freq_colors_indices]
    sorted_most_freq_colors_counts = unique_counts[sorted_most_freq_colors_indices]
    sorted_most_freq_colors_counts_normed = sorted_most_freq_colors_counts / np.sum(sorted_most_freq_colors_counts)
    # print(sorted_most_freq_colors.shape, sorted_most_freq_colors)
    normed_hist = build_histogram_html(sorted_most_freq_colors, sorted_most_freq_colors_counts_normed)
    return normed_hist


def build_histogram_html(sorted_most_freq_colors: np.ndarray, sorted_most_freq_colors_counts_normed: np.ndarray) -> str:
    max_points = 20
    bars = []
    for color, fraction in zip(sorted_most_freq_colors, sorted_most_freq_colors_counts_normed):
        npoints = '.' * int(fraction * max_points)
        if isinstance(color, np.ndarray):
            color_rgba = tuple(color)
        else:
            color_rgba = (color, color, color, 255)
        inverse_color_rgba = (255 - color_rgba[0], 255 - color_rgba[1], 255 - color_rgba[2], 255)
        fraction_percent = int(fraction * 100)
        bar_html = f'<div style="background-color: rgba{color_rgba}; color: rgba{inverse_color_rgba}">{fraction_percent}%{npoints}</div>'
        bars.append(bar_html)
    histogram_html = '<div>' + '\n'.join(bars) + '</div>'
    return histogram_html
