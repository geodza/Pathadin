from PyQt5.QtWidgets import QItemEditorFactory, QWidget, QItemEditorCreatorBase


class CustomItemEditorFactory(QItemEditorFactory):

    def __init__(self, system_item_editor_factory: QItemEditorFactory, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.custom_editor_factories = {}
        self.system_item_editor_factory = system_item_editor_factory

    def createEditor(self, userType: int, parent: QWidget) -> QWidget:
        if userType in self.custom_editor_factories:
            factory = self.custom_editor_factories[userType]
            return factory.createEditor(userType, parent)
        else:
            return self.system_item_editor_factory.createEditor(userType, parent)

    def registerEditor(self, userType: int, creator: QItemEditorCreatorBase) -> None:
        factory = QItemEditorFactory()
        factory.registerEditor(userType, creator)
        self.custom_editor_factories[userType] = factory