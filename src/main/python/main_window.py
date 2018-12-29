from functools import partial

from PyQt5.QtCore import Qt, QThread
from PyQt5.QtWidgets import (QComboBox, QFormLayout, QFrame, QGridLayout,
                             QGroupBox, QHBoxLayout, QLabel, QLineEdit,
                             QMainWindow, QProgressBar, QPushButton, QSpinBox,
                             QSystemTrayIcon, QTextEdit, QVBoxLayout, QWidget)

import utils
from constants import (APPLICATION_NAME, COURSE_LIST_TITLE,
                       COURSE_STRUCTURE_TITLE, DASHBOARD_LABEL, FONT_NAME,
                       FONT_SIZE, FORM_HORIZONTAL_SPACING,
                       FORM_VERTICAL_SPACING, HORIZONTAL_SPACING,
                       PASSWORD_LABEL, PROGRESSBAR_LABEL, START_BUTTON_LABEL,
                       STOP_BUTTON_LABEL, TIME_INPUT_LABEL, TIME_LIMIT_MAXIMUM,
                       TIME_LIMIT_MINIMUM, USERNAME_LABEL, VERTICAL_SPACING,
                       WEBSITE_CHOOSER_LABEL, WEBSITE_LOGIN_LABEL,
                       WEBSITE_URL_LABEL, WINDOW_SIZE)
from course_list import CourseListView
from course_structure import CourseStructure
from session import Session


class DownloaderWindow(QMainWindow):
    def __init__(self, app, application_context):
        super().__init__()
        self.app = app
        self.application_context = application_context
        self.configuration = application_context.configuration
        self.init_UI()

        self.configure_session()

        self.connect_events()

    def init_UI(self):
        self.setWindowTitle(APPLICATION_NAME)
        self.setMinimumSize(*WINDOW_SIZE)
        # self.showMaximized()

        self.grid = QGridLayout()
        self.grid.setVerticalSpacing(VERTICAL_SPACING)
        self.grid.setHorizontalSpacing(HORIZONTAL_SPACING)

        self.create_website_login()
        self.create_dashboard()
        self.create_progressbar()

        centralWidget = QWidget()
        centralWidget.setLayout(self.grid)
        self.setCentralWidget(centralWidget)

    def configure_session(self):
        self.session = Session(
            self.configuration, self.website_input.currentText())
        self.processing_thread = QThread()
        self.session.moveToThread(self.processing_thread)
        self.processing_thread.start()

    def connect_events(self):
        self.website_input.activated[str].connect(self.website_changed)
        self.login_btn.clicked.connect(partial(self.session.login, username=self.username_input, password=self.password_input))
        self.session.login_successful.connect(self.login_successful)

    def _create_website_form(self, groupbox):
        website_chooser_label = QLabel(WEBSITE_CHOOSER_LABEL)
        self.website_input = QComboBox(groupbox)

        self.website_input, self.website_url_map = self.configuration.populate_website_chooser(
            self.website_input)
        website_url_label = QLabel(WEBSITE_URL_LABEL)
        self.website_url_input = QLineEdit(groupbox)
        self.website_url_input.setText(
            self.website_url_map[str(self.website_input.currentText())])
        self.website_url_input.setDisabled(True)

        left_panel = QFrame(groupbox)
        left_panel.setFrameStyle(QFrame.StyledPanel)
        left_form = QFormLayout()
        left_form.setHorizontalSpacing(FORM_HORIZONTAL_SPACING)
        left_form.setVerticalSpacing(FORM_VERTICAL_SPACING)
        left_form.addRow(website_chooser_label, self.website_input)
        left_form.addRow(website_url_label, self.website_url_input)
        left_panel.setLayout(left_form)

        return left_panel

    def _create_login_form(self, groupbox):
        vbox = QVBoxLayout()

        username_label = QLabel(USERNAME_LABEL)
        self.username_input = QLineEdit(groupbox)
        password_label = QLabel(PASSWORD_LABEL)
        self.password_input = QLineEdit(groupbox)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.login_btn = QPushButton('Login', groupbox)

        hbox_btn = QHBoxLayout()
        hbox_btn.addStretch(1)
        hbox_btn.addWidget(self.login_btn)

        right_panel = QFrame(groupbox)
        right_panel.setFrameStyle(QFrame.StyledPanel)
        right_form = QFormLayout()
        right_form.setHorizontalSpacing(FORM_HORIZONTAL_SPACING)
        right_form.setVerticalSpacing(FORM_VERTICAL_SPACING)
        right_form.addRow(username_label, self.username_input)
        right_form.addRow(password_label, self.password_input)

        vbox.addLayout(right_form)
        vbox.addStretch(1)
        vbox.addLayout(hbox_btn)
        right_panel.setLayout(vbox)

        return right_panel

    def create_website_login(self):
        groupbox = QGroupBox(WEBSITE_LOGIN_LABEL)
        hbox = QHBoxLayout()

        left_panel = self._create_website_form(groupbox)
        right_panel = self._create_login_form(groupbox)

        hbox.addWidget(left_panel)
        hbox.addWidget(right_panel)

        groupbox.setLayout(hbox)
        self.grid.addWidget(groupbox, 0, 0, 3, 12)

    def create_course_list(self, groupbox):
        vbox = QVBoxLayout()

        left_panel = QFrame(groupbox)
        left_panel.setFrameStyle(QFrame.StyledPanel)

        title_label = QLabel(COURSE_LIST_TITLE)
        self.course_list = CourseListView()

        vbox.addWidget(title_label)
        vbox.addWidget(self.course_list)
        left_panel.setLayout(vbox)
        return left_panel

    def create_video_tree(self, groupbox):
        vbox = QVBoxLayout()

        right_panel = QFrame(groupbox)
        right_panel.setFrameStyle(QFrame.StyledPanel)
        title_label = QLabel(COURSE_STRUCTURE_TITLE)
        self.course_structure = CourseStructure()

        vbox.addWidget(title_label)
        vbox.addWidget(self.course_structure)
        right_panel.setLayout(vbox)
        return right_panel

    def create_dashboard(self):
        groupbox = QGroupBox(DASHBOARD_LABEL)
        mini_grid = QGridLayout()

        left_panel = self.create_course_list(groupbox)
        right_panel = self.create_video_tree(groupbox)
        self.action_button = QPushButton("Action")
        self.cancel_button = QPushButton("Cancel")

        mini_grid.addWidget(left_panel, 0, 0, 5, 3)
        mini_grid.addWidget(right_panel, 0, 3, 5, 6)
        mini_grid.addWidget(self.action_button, 5, 7, 1, 1)
        mini_grid.addWidget(self.cancel_button, 5, 8, 1, 1)
        groupbox.setLayout(mini_grid)

        self.grid.addWidget(groupbox, 3, 0, 8, 12)

    def create_progressbar(self):
        groupbox = QGroupBox(PROGRESSBAR_LABEL)
        self.progressbar = QProgressBar(groupbox)
        self.progressbar.setMaximum(100)
        self.progressbar.setMinimum(0)
        self.progressbar.setValue(50)
        vbox = QVBoxLayout()
        vbox.addWidget(self.progressbar)
        groupbox.setLayout(vbox)
        self.grid.addWidget(groupbox, 11, 0, 1, 12)

    def website_changed(self, website_name):
        self.website_url_input.setText(self.website_url_map[website_name])
        self.session.change_website(website_name)

    def login(self):
        self.session.login(self.username_input.text(),
                           self.password_input.text())

    def login_successful(self, successful):
        print(successful, flush=True)
