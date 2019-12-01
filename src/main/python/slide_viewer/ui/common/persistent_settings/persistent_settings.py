from PyQt5.QtCore import QSettings


def write_settings(app_name, group_name, dict_: dict):
    settings = QSettings(app_name, app_name)
    settings.beginGroup(group_name)
    for key, value in dict_.items():
        # if isinstance(value,Iterable):
        #     value_list=list(value)
        #     settings.beginWriteArray()
        # settings.setValue("size", self.size())
        settings.setValue(key, value)
    settings.endGroup()


def read_settings(app_name, group_name) -> dict:
    settings = QSettings(app_name, app_name)
    settings.beginGroup(group_name)
    dict_ = {}
    for key in settings.allKeys():
        value = settings.value(key)
        dict_[key] = value
    settings.endGroup()
    return dict_
