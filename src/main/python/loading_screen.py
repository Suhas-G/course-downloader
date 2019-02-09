from PyQt5.QtCore import QByteArray, Qt
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout


class LoadingScreen(QDialog):
    def __init__(self, parent, file_path, text):
        """Initialise the loading screen
        
        Arguments:
            parent {QObject} -- The parent QObject
            file_path {str} -- Path to file of loading GIF
            text {str} -- Text to be shown on the loading screen
        """
        super().__init__(parent)
        self.file = file_path
        self.text = text
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setFixedSize(200, 200)
        self.setModal(True)
        self.init_UI()

    def init_UI(self):
        """Initialise the UI by loading the GIF and adding the text label
        """
        vbox = QVBoxLayout()
        vbox.setAlignment(Qt.AlignHCenter)
        self.movie_screen = QLabel(self)
        self.movie_screen.setFixedSize(50, 50)

        self.movie = QMovie(self.file, QByteArray(), self)
        self.movie.setScaledSize(self.movie_screen.size())
        self.movie.setCacheMode(QMovie.CacheAll)
        self.movie.setSpeed(100)
        self.movie_screen.setMovie(self.movie)
        self.movie.start()
        self.movie.loopCount()

        self.loading = QLabel(self.text)
        self.loading.setAlignment(Qt.AlignCenter)
        vbox.addStretch(2)
        vbox.addWidget(self.movie_screen, Qt.AlignCenter)
        vbox.addSpacing(10)
        vbox.addWidget(self.loading, Qt.AlignHCenter)
        vbox.addStretch(1)
        self.setLayout(vbox)
