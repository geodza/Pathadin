from PyQt5.QtWidgets import QDialog, QSpinBox, QHBoxLayout, QFormLayout, QVBoxLayout, QDialogButtonBox

from slide_viewer.ui.slide.graphics.slide_graphics_grid_item import SlideGraphicsGridItem


def on_grid_change_size(grid_item: SlideGraphicsGridItem):
    if not grid_item:
        return
    dialog = QDialog()
    dialog.setWindowTitle("Grid size")
    grid_size = grid_item.grid_size
    grid_w = QSpinBox()
    grid_w.setMaximum(2 ** 15)
    grid_w.setValue(grid_size[0])
    grid_h = QSpinBox()
    grid_h.setMaximum(2 ** 15)
    grid_h.setValue(grid_size[1])
    horizontal_layout = QHBoxLayout()
    horizontal_layout.addWidget(grid_w)
    horizontal_layout.addWidget(grid_h)
    form_layout = QFormLayout()
    form_layout.addRow("grid width:", horizontal_layout)

    main_layout = QVBoxLayout()
    main_layout.addLayout(form_layout)
    button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
    main_layout.addWidget(button_box)
    dialog.setLayout(main_layout)
    button_box.accepted.connect(dialog.accept)
    button_box.rejected.connect(dialog.reject)
    res = dialog.exec()
    if res == QDialog.Accepted:
        grid_item.grid_size = (grid_w.value(), grid_h.value())
        grid_item.update_lines()
        grid_item.update()
