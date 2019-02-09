from PyQt5.QtWidgets import QMessageBox, QSizePolicy

from constants import CRITICAL, INFORMATION, WARNING


class MessageDialog(QMessageBox):
    def __init__(self, title, text, message_type=WARNING, informativeText='', callback=None):
        """Initialise dialog box
        
        Arguments:
            title {str} -- The title of the dialog
            text {str} -- The summary of the dialog
        
        Keyword Arguments:
            message_type {str} -- Type of message to show appropriate icon on the dialog (default: {WARNING})
            informativeText {str} -- More info text to be displayed (default: {''})
            callback {function} -- Function to be called when the dialog is dismissed (default: {None})
        """
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
