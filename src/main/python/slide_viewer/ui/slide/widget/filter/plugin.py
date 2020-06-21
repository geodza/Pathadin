import importlib
import inspect
import pkgutil
import sys
import typing

from filter.filter_plugin import FilterPlugin
from filter.pathadin_gray_manual_threshold_filter_plugin import GrayManualThresholdFilterPlugin
from filter.pathadin_hsv_manual_threshold_filter_plugin import HSVManualThresholdFilterPlugin
from filter.pathadin_keras_model_filter_plugin import KerasModelFilterPlugin
from filter.pathadin_kmeans_filter_plugin import KMeansFilterPlugin
from filter.pathadin_nuclei_filter_plugin import NucleiFilterPlugin
from filter.pathadin_positive_pixel_count_filter_plugin import PositivePixelCountFilterPlugin
from filter.pathadin_skimage_threshold_filter_plugin import SkimageThresholdFilterPlugin

F = typing.TypeVar('F', bound=FilterPlugin)


def load_filter_plugin_clazzes() -> typing.List[typing.Type[F]]:
	path_ = sys.path
	top_level_items = list(name for finder, name, ispkg in pkgutil.iter_modules())
	pathadin_top_level_items = list(n for n in top_level_items if n.startswith("pathadin"))
	discovered_plugins = {
		name: importlib.import_module(name)
		for finder, name, ispkg
		in pkgutil.iter_modules()
		if name.startswith('pathadin') and not ispkg
	}
	filter_plugin_clazzes = []
	for module_name, module in discovered_plugins.items():
		for clazz_name, clazz in inspect.getmembers(module, inspect.isclass):
			if issubclass(clazz, FilterPlugin) and getattr(clazz, 'plugin', False):
				print(f'Found plugin class: {clazz.__module__}.{clazz.__name__}')
				filter_plugin_clazzes.append(clazz)
	filter_plugin_clazzes = [GrayManualThresholdFilterPlugin, HSVManualThresholdFilterPlugin, KerasModelFilterPlugin,
							 KMeansFilterPlugin, NucleiFilterPlugin, PositivePixelCountFilterPlugin,
							 SkimageThresholdFilterPlugin]
	return filter_plugin_clazzes


def load_filter_plugins() -> typing.List[FilterPlugin]:
	filter_plugin_clazzes = load_filter_plugin_clazzes()
	filter_plugins = []
	for clazz in filter_plugin_clazzes:
		filter_plugin = clazz()
		print(f'Plugin created: {filter_plugin}')
		filter_plugins.append(filter_plugin)

	return filter_plugins
