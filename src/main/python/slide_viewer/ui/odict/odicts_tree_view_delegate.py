from PyQt5 import QtCore
from PyQt5.QtCore import QModelIndex, QObject, QSize
from PyQt5.QtWidgets import QWidget, QStyledItemDelegate, \
    QStyleOptionViewItem

from slide_viewer.ui.common.editor.color_editor import ColorEditor
from slide_viewer.ui.common.editor.dropdown import Dropdown
from slide_viewer.ui.common.editor.list_editor import SelectListEditor
from slide_viewer.ui.common.editor.range.gray_range_editor import GrayRangeEditor
from slide_viewer.ui.common.editor.range.hsv_range_editor import HSVRangeEditor
from img.filter.threshold_filter import ThresholdFilterData_, ThresholdType
from img.filter.skimage_threshold import SkimageThresholdType, SkimageAutoThresholdFilterData_
from img.filter.manual_threshold import ManualThresholdFilterData_
from img.filter.base_filter import FilterData_, FilterType
from img.color_mode import ColorMode


class ODictsTreeViewDelegate(QStyledItemDelegate):

    def __init__(self, parent: QObject = None) -> None:
        super().__init__(parent)

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex) -> QWidget:
        if ODictsTreeModel.is_attr(index) and ODictsTreeModel.is_attr_value(index):
            model: ODictsTreeModel = index.model()
            odict_number = index.parent().row()
            odict = model.get_odict(odict_number)
            attr_key = model.get_attr_key(index.parent().row(), index.row())
            attr_value = odict[attr_key]
            color_attr_key_handlers = [ODictModel.odict_background_attr, ODictModel.odict_decoration_attr]
            color_attr_keys = set(odict.get(attr_handler) for attr_handler in color_attr_key_handlers)
            if attr_key in color_attr_keys:
                return ColorEditor(None, parent)
            list_attr_keys = [ODictModel.odict_display_attrs, ODictModel.odict_hidden_attrs]
            if attr_key in list_attr_keys:
                all_values = [key for key in odict if key != ODictModel.odict_hidden_attrs]
                return SelectListEditor(all_values, parent)
            # TODO because of flat structure, naming conflicts are possible. Change to filter_type, or implement nested odict model, or store odict filter_type (annotation, template, or filter)
            name_to_enum = {
                FilterData_.filter_type: FilterType,
                ThresholdFilterData_.threshold_type: ThresholdType,
                SkimageAutoThresholdFilterData_.skimage_threshold_type: SkimageThresholdType,
                ManualThresholdFilterData_.color_mode: ColorMode,
                QuantizationFilterData_.method: PillowQuantizeMethod
            }
            if attr_key in name_to_enum:
                enum_ = name_to_enum[attr_key]
                items = list(enum_)
                dropdown = Dropdown(items, attr_value, parent)

                def on_selected_item_changed(item):
                    self.commitData.emit(dropdown)
                    self.closeEditor.emit(dropdown)

                dropdown.selectedItemChanged.connect(on_selected_item_changed)
                dropdown.activated.connect(on_selected_item_changed)
                return dropdown
            elif attr_key == ManualThresholdFilterData_.threshold_range:
                def on_threshold_range_change(range_):
                    model.edit_attr_by_key(odict_number, ManualThresholdFilterData_.threshold_range, range_)

                if odict[ManualThresholdFilterData_.color_mode] == ColorMode.HSV:
                    # self.sizeHintChanged.emit(index.sibling(index.row() + 1, index.column()))
                    editor = HSVRangeEditor(parent)
                    editor.hsvRangeChanged.connect(on_threshold_range_change)
                    return editor
                elif odict[ManualThresholdFilterData_.color_mode] == ColorMode.L:
                    # self.sizeHintChanged.emit(index.sibling(index.row() + 1, index.column()))
                    editor = GrayRangeEditor(parent)
                    editor.grayRangeChanged.connect(on_threshold_range_change)
                    return editor

        return super().createEditor(parent, option, index)

    # def setEditorData(self, editor: QWidget, index: QtCore.QModelIndex) -> None:
    #     super().setEditorData(editor, index)

    # def setModelData(self, editor: QWidget, model: QtCore.QAbstractItemModel, index: QtCore.QModelIndex) -> None:
    #     super().setModelData(editor, model, index)

    def updateEditorGeometry(self, editor: QWidget, option: QStyleOptionViewItem, index: QtCore.QModelIndex) -> None:
        if isinstance(editor, (SelectListEditor, HSVRangeEditor)):
            # editor.setMinimumHeight(400)
            super().updateEditorGeometry(editor, option, index)
            # editor.setGeometry(option.rect)
            # editor.layout().setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
            # editor.set(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
            if isinstance(editor, SelectListEditor):
                editor.adjustSize()
            # editor.update()
        elif isinstance(editor, Dropdown):
            super().updateEditorGeometry(editor, option, index)
            editor.showPopup()
        else:
            super().updateEditorGeometry(editor, option, index)

    def editorEvent(self, event: QtCore.QEvent, model: QtCore.QAbstractItemModel, option: QStyleOptionViewItem,
                    index: QtCore.QModelIndex) -> bool:
        # print(event, index, option.type, option.widget, option.state)
        # print(option.state & QStyle.State_Editing == QStyle.State_Editing)
        # print(option.state, int(option.state), hex(option.state))
        return super().editorEvent(event, model, option, index)

    def sizeHint(self, option: QStyleOptionViewItem, index: QtCore.QModelIndex) -> QtCore.QSize:
        if ODictsTreeModel.is_attr(index) and ODictsTreeModel.is_attr_value(index):
            model: ODictsTreeModel = index.model()
            odict = model.get_odict(index.parent().row())
            attr_key = model.get_attr_key(index.parent().row(), index.row())
            # print(index.data(Qt.SizeHintRole), option.rect)
            if attr_key == 'threshold_range':
                color_mode_to_size = {
                    ColorMode.HSV: QSize(0, 250),
                    ColorMode.L: QSize(0, 250),
                }
                return color_mode_to_size[odict['color_mode']]
            return super().sizeHint(option, index)
        else:
            return super().sizeHint(option, index)
