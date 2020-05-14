from PyQt5.QtCore import QMimeData


def mime_data_is_url(mime_data: QMimeData):
    return mime_data.hasUrls() and len(mime_data.urls()) == 1