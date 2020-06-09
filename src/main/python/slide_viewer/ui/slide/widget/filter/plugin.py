import importlib
import inspect
import pkgutil
import typing

from filter.filter_plugin import FilterPlugin

F = typing.TypeVar('F', bound=FilterPlugin)


def load_filter_plugin_clazzes() -> typing.List[typing.Type[F]]:
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
	return filter_plugin_clazzes


def load_filter_plugins() -> typing.List[FilterPlugin]:
	filter_plugin_clazzes = load_filter_plugin_clazzes()
	filter_plugins = []
	for clazz in filter_plugin_clazzes:
		filter_plugin = clazz()
		print(f'Plugin created: {filter_plugin}')
		filter_plugins.append(filter_plugin)

	return filter_plugins
