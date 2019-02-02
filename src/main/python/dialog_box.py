from PyQt5.QtWidgets import QMessageBox, QSizePolicy

from constants import CRITICAL, INFORMATION, WARNING


class MessageDialog(QMessageBox):
    def __init__(self, title, text, message_type=WARNING, informativeText='', callback=None):
        super().__init__()

        if not getattr(QMessageBox, message_type, None) is None:
            self.setIcon(getattr(QMessageBox, message_type))
        else:
            self.setIcon(getattr(QMessageBox, WARNING))

        self.setWindowTitle(title)
        self.setText(text)

        if informativeText != '':
            self.setInformativeText(informativeText)

        self.setStandardButtons(QMessageBox.Ok)
        if not callback is None:
            self.buttonClicked.connect(callback)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.adjustSize()
