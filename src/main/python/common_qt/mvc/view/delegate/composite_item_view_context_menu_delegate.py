import typing
from abc import ABC

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QModelIndex, Qt, QAbstractItemModel
from PyQt5.QtWidgets import QStyledItemDelegate, QWidget, QItemEditorFactory, QStyleOptionViewItem, QAbstractItemView, \
	QMenu, QAction
from dataclasses import dataclass, field

from common_qt.mvc.view.delegate.abstract_item_view_context_menu_delegate import AbstractItemViewContextMenuDelegate
from common_qt.mvc.view.delegate.factory.abstract_item_view_context_menu_delegate_factory import \
	AbstractItemViewContextMenuDelegateFactory

I = typing.TypeVar('I', bound=QModelIndex)
V = typing.TypeVar('V', bound=QAbstractItemView)


class CompositeItemViewContextMenuDelegate(AbstractItemViewContextMenuDelegate, typing.Generic[I, V]):

	def __init__(self, view: V, factories: typing.List[AbstractItemViewContextMenuDelegateFactory[I, V]] = []):
		super().__init__(view)
		self.factories = factories

	def find_delegate(self, index: I) -> AbstractItemViewContextMenuDelegate:
		for f in self.factories:
			d = f.create_delegate(index, self.view)
			if d is not None:
				return d
		raise ValueError(f"CompositeItemViewDelegate. No appropriate delegate found in {self.factories}")

	def find_delegates(self, index: I) -> typing.List[AbstractItemViewContextMenuDelegate]:
		delegates = []
		for f in self.factories:
			d = f.create_delegate(index, self.view)
			if d is not None:
				delegates.append(d)
		return delegates

	def create_menu(self, index: I) -> QMenu:
		if index.isValid():
			print("create menu with delegate")
			return self.find_delegate(index).create_menu(index)
		else:
			menus = [d.create_menu(index) for d in self.find_delegates(index)]
			print("create menu with delegates", len(menus))
			menu = QMenu()
			for i, m in enumerate(menus):
				menu.addMenu(m)
			menu.menus_ref_hack = menus

			return menu
