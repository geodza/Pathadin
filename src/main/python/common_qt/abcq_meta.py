import abc

from PyQt5.QtCore import QObject
# from pydantic import BaseModel


class ABCQMeta(type(QObject), type(abc.ABC)):
    pass


# class BaseModelQMeta(type(QObject), type(BaseModel)):
#     pass

class QABCMeta(type(QObject), abc.ABCMeta):
    pass