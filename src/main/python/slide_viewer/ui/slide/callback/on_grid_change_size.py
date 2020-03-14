from PyQt5.QtCore import QMargins
from PyQt5.QtWidgets import QDialog, QSpinBox, QHBoxLayout, QFormLayout, QVBoxLayout, QDialogButtonBox, QRadioButton, QButtonGroup, QWidget, QLabel

from common_qt.slot_disconnected_utils import slot_disconnected
from slide_viewer.ui.slide.graphics.view.graphics_view import GraphicsView


def on_grid_change_size(view: GraphicsView) -> None:
    dialog = QDialog()
    dialog.setWindowTitle("Grid size")
    if view.get_grid_size_is_in_pixels():
        grid_size_pixels = view.get_grid_size()
        w, h = grid_size_pixels
        grid_size_microns = (view.slide_helper.pixels_to_microns(w), view.slide_helper.pixels_to_microns(h))
    else:
        grid_size_microns = view.get_grid_size()
        w, h = grid_size_microns
        grid_size_pixels = (view.slide_helper.microns_to_pixels(w), view.slide_helper.microns_to_pixels(h))

    form_layout = QFormLayout()

    def update_microns_by_pixels(v):
        with slot_disconnected(grid_w_microns.valueChanged, update_pixels_by_microns):
            grid_w_microns.setValue(view.slide_helper.pixels_to_microns(grid_w_pixels.value()))
        with slot_disconnected(grid_h_microns.valueChanged, update_pixels_by_microns):
            grid_h_microns.setValue(view.slide_helper.pixels_to_microns(grid_h_pixels.value()))

    def update_pixels_by_microns(v):
        with slot_disconnected(grid_w_pixels.valueChanged, update_microns_by_pixels):
            grid_w_pixels.setValue(view.slide_helper.microns_to_pixels(grid_w_microns.value()))
        with slot_disconnected(grid_h_pixels.valueChanged, update_microns_by_pixels):
            grid_h_pixels.setValue(view.slide_helper.microns_to_pixels(grid_h_microns.value()))

    grid_w_pixels = QSpinBox()
    grid_w_pixels.setMaximum(2 ** 15)
    grid_w_pixels.setValue(grid_size_pixels[0])
    grid_w_pixels.valueChanged.connect(update_microns_by_pixels)
    grid_h_pixels = QSpinBox()
    grid_h_pixels.setMaximum(2 ** 15)
    grid_h_pixels.setValue(grid_size_pixels[1])
    grid_h_pixels.valueChanged.connect(update_microns_by_pixels)
    horizontal_layout_pixels = QHBoxLayout()
    horizontal_layout_pixels.addWidget(grid_w_pixels)
    horizontal_layout_pixels.addWidget(grid_h_pixels)
    parent_pixels = QWidget()
    horizontal_layout_pixels.setContentsMargins(QMargins())
    parent_pixels.setLayout(horizontal_layout_pixels)

    form_layout.addRow("Grid (width, height) in pixels:", parent_pixels)

    grid_w_microns = QSpinBox()
    grid_w_microns.setMaximum(2 ** 15)
    grid_w_microns.setValue(grid_size_microns[0])
    grid_w_microns.valueChanged.connect(update_pixels_by_microns)
    grid_h_microns = QSpinBox()
    grid_h_microns.setMaximum(2 ** 15)
    grid_h_microns.setValue(grid_size_microns[1])
    grid_h_microns.valueChanged.connect(update_pixels_by_microns)
    horizontal_layout_microns = QHBoxLayout()
    horizontal_layout_microns.addWidget(grid_w_microns)
    horizontal_layout_microns.addWidget(grid_h_microns)
    parent_microns = QWidget()
    horizontal_layout_microns.setContentsMargins(QMargins())
    parent_microns.setLayout(horizontal_layout_microns)
    form_layout.addRow("Grid (width, height) in microns:", parent_microns)

    radio_group = QButtonGroup()
    pixels_button = QRadioButton("pixels")
    microns_button = QRadioButton("microns")
    radio_group.addButton(pixels_button)
    radio_group.addButton(microns_button)

    def on_pixels_button_toggle(v):
        parent_pixels.setEnabled(v)

    def on_microns_button_toggle(v):
        parent_microns.setEnabled(v)

    pixels_button.toggled.connect(on_pixels_button_toggle)
    microns_button.toggled.connect(on_microns_button_toggle)
    if view.get_grid_size_is_in_pixels():
        pixels_button.setChecked(True)
        parent_microns.setEnabled(False)
    else:
        microns_button.setChecked(True)
        parent_pixels.setEnabled(False)
    radio_layout = QHBoxLayout()
    radio_layout.addWidget(pixels_button)
    radio_layout.addWidget(microns_button)
    form_layout.addRow("Grid size unit:", radio_layout)
    form_layout.addRow("Microns per pixel:", QLabel(f"{view.slide_helper.microns_per_pixel}"))

    main_layout = QVBoxLayout()
    main_layout.addLayout(form_layout)
    button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
    main_layout.addWidget(button_box)
    dialog.setLayout(main_layout)
    button_box.accepted.connect(dialog.accept)
    button_box.rejected.connect(dialog.reject)
    res = dialog.exec()
    if res == QDialog.Accepted:
        if pixels_button.isChecked():
            grid_size = (grid_w_pixels.value(), grid_h_pixels.value())
            grid_size_is_in_pixels = True
        else:
            grid_size = (grid_w_microns.value(), grid_h_microns.value())
            grid_size_is_in_pixels = False

        view.set_grid_size(grid_size)
        view.set_grid_size_is_in_pixels(grid_size_is_in_pixels)
