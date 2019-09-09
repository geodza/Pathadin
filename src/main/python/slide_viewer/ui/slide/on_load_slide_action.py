from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFileDialog

from slide_viewer.ui.common.my_action import MyAction


class SelectSlideFileAction(MyAction):
    def __init__(self, title, parent, callback, icon: QIcon):
        super().__init__(title, parent, self.on_select_slide_file, icon)
        self.callback = callback

    def on_select_slide_file(self):
        file_path = self.open_file_name_dialog()
        if file_path:
            self.callback(file_path)

    def get_available_formats(self):
        whole_slide_formats = [
            "svs",
            "vms",
            "vmu",
            "ndpi",
            "scn",
            "mrx",
            "tiff",
            "svslide",
            "tif",
            "bif",
            "mrxs",
            "bif"]
        pillow_formats = [
            'bmp', 'bufr', 'cur', 'dcx', 'fits', 'fl', 'fpx', 'gbr',
            'gd', 'gif', 'grib', 'hdf5', 'ico', 'im', 'imt', 'iptc',
            'jpeg', 'jpg', 'jpe', 'mcidas', 'mic', 'mpeg', 'msp',
            'pcd', 'pcx', 'pixar', 'png', 'ppm', 'psd', 'sgi',
            'spider', 'tga', 'tiff', 'wal', 'wmf', 'xbm', 'xpm',
            'xv'
        ]
        available_formats = [*whole_slide_formats, *pillow_formats]
        available_extensions = ["." + available_format for available_format in available_formats]
        return available_extensions

    def open_file_name_dialog(self):
        # print(tuple([e[1:] for e in PIL.Image.EXTENSION]))
        options = QFileDialog.Options()
        file_ext_strings = ["*" + ext for ext in self.get_available_formats()]
        file_ext_string = " ".join(file_ext_strings)
        file_name, _ = QFileDialog.getOpenFileName(self.window, "Select whole-slide image to view", "",
                                                   "Whole-slide images ({});;".format(file_ext_string),
                                                   options=options)
        return file_name
