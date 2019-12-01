from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, QVBoxLayout, QTextEdit


class DynamicCommandWidget(QWidget):
    def __init__(self, ref: QWidget):
        super().__init__()
        self.ref = ref
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        self.dynamic_command_line_edit = QTextEdit()
        # self.dynamic_command_line_edit.returnPressed.connect(self.on_execute_command_text)
        button1 = QPushButton("Exec")
        button1.clicked.connect(self.on_execute_command_text)
        layout.addWidget(self.dynamic_command_line_edit)
        layout.addWidget(button1)

    def on_execute_command_text(self):
        dynamic_command_text = self.dynamic_command_line_edit.toPlainText()
        print("exec", dynamic_command_text)
        exec(dynamic_command_text)
