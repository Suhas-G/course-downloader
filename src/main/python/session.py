from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QLineEdit

from edx_downloader import EdXDownloader


class Session(QObject):

    login_successful = pyqtSignal(bool)

    def __init__(self, configuration, website_name):
        super().__init__()
        self.configuration = configuration
        self.website = website_name
        self.set_downloader(website_name)

    def change_website(self, website_name):
        self.website = website_name
        self.set_downloader(website_name)

    def set_downloader(self, website_name):
        if website_name == "edX":
            self.downloader = EdXDownloader(self.configuration)
        else:
            self.downloader = None

    def set_credentials(self, username, password):
        self.username = username
        self.password = password

    @pyqtSlot('QLineEdit', 'QLineEdit')
    def login(self, username, password):
        successful = self.downloader.login(username.text(), password.text())
        self.login_successful.emit(successful)
