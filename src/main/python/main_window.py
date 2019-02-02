from functools import partial

from PyQt5.QtCore import Qt, QThread
from PyQt5.QtWidgets import (QComboBox, QFileDialog, QFormLayout, QFrame,
                             QGridLayout, QGroupBox, QHBoxLayout, QLabel,
                             QLineEdit, QMainWindow, QProgressBar, QPushButton,
                             QSpinBox, QSystemTrayIcon, QTextEdit, QToolButton,
                             QVBoxLayout, QWidget)

import utils
from constants import (APPLICATION_NAME, BROWSE_LABEL, CANCEL_LABEL,
                       CANCELLING_LABEL, COURSE_LIST_TITLE,
                       COURSE_STRUCTURE_TITLE, CRITICAL, DASHBOARD_LABEL,
                       DOWNLOAD_COURSES_LABEL, FORM_HORIZONTAL_SPACING,
                       FORM_VERTICAL_SPACING, HORIZONTAL_SPACING, INFORMATION,
                       LOADING_GIF, LOADING_LABEL, LOGIN_LABEL, PASSWORD_LABEL,
                       PROGRESSBAR_LABEL, PROGRESSBAR_MAXIMUM,
                       PROGRESSBAR_MINIMUM, RETRIEVE_COURSES_LABEL,
                       ROOT_FOLDER_LABEL, USERNAME_LABEL, VERTICAL_SPACING,
                       WARNING, WEBSITE_CHOOSER_LABEL, WEBSITE_LOGIN_LABEL,
                       WEBSITE_URL_LABEL, WINDOW_SIZE)
from course_list import CourseListView
from course_structure import CourseStructure
from dialog_box import MessageDialog
from loading_screen import LoadingScreen
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
        self.showMaximized()

        self.grid = QGridLayout()
        self.grid.setVerticalSpacing(VERTICAL_SPACING)
        self.grid.setHorizontalSpacing(HORIZONTAL_SPACING)

        self.create_website_login()
        self.create_dashboard()
        self.create_progressbar()

        centralWidget = QWidget()
        centralWidget.setLayout(self.grid)
        self.loading_screen = LoadingScreen(centralWidget, 
                                self.application_context.get_resource(LOADING_GIF),
                                LOADING_LABEL)
        self.setCentralWidget(centralWidget)

    def configure_session(self):
        self.session = Session(
            self.configuration, self.application_context, self.website_input.currentText())
        self.processing_thread = QThread()
        self.session.moveToThread(self.processing_thread)
        self.processing_thread.start()

    def connect_events(self):
        self.website_input.activated[str].connect(self.website_changed)
        self.login_btn.clicked.connect(partial(
            self.session.login, username=self.username_input, password=self.password_input))
        self.root_folder_path_button.clicked.connect(self.get_root_folder)
        self.session.login_successful.connect(self.login_successful)
        self.session.courses_retrieved.connect(self.courses_retrieved)
        self.action_button.clicked.connect(partial(self.session.action_button_clicked, self.course_list, 
                                                    self.action_button, self.root_folder_path_input))
        self.cancel_button.clicked.connect(self.cancel_pressed)
        self.session.loading_screen.connect(self.show_loading_screen)
        self.session.clear_course_list.connect(self.course_list.clear_all)
        self.session.clear_course_structure.connect(self.course_structure.clear)
        self.session.courses_downloaded.connect(self.courses_downloaded)
        self.session.download_progress.connect(self.download_progress)
        self.session.destination_required.connect(self.raise_error_dialog)
        self.session.course_selection_required.connect(self.raise_error_dialog)

    def show_loading_screen(self, show):
        if show:
            self.loading_screen.open()
        else:
            self.loading_screen.close()

    def create_website_form(self, groupbox):
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

    def create_login_form(self, groupbox):
        vbox = QVBoxLayout()

        username_label = QLabel(USERNAME_LABEL)
        self.username_input = QLineEdit(groupbox)
        password_label = QLabel(PASSWORD_LABEL)
        self.password_input = QLineEdit(groupbox)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.login_btn = QPushButton(LOGIN_LABEL, groupbox)

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

        left_panel = self.create_website_form(groupbox)
        right_panel = self.create_login_form(groupbox)

        hbox.addWidget(left_panel)
        hbox.addWidget(right_panel)

        groupbox.setLayout(hbox)
        self.grid.addWidget(groupbox, 0, 0, 3, 12)

    def create_course_list(self, groupbox):
        vbox = QVBoxLayout()

        left_panel = QFrame(groupbox)
        left_panel.setFrameStyle(QFrame.StyledPanel)

        title_label = QLabel(COURSE_LIST_TITLE)
        self.course_list = CourseListView(self)

        vbox.addWidget(title_label)
        vbox.addWidget(self.course_list)
        left_panel.setLayout(vbox)
        return left_panel

    def create_video_tree(self, groupbox):
        vbox = QVBoxLayout()

        right_panel = QFrame(groupbox)
        right_panel.setFrameStyle(QFrame.StyledPanel)

        root_folder_label = QLabel(ROOT_FOLDER_LABEL)
        self.root_folder_path_input = QLineEdit()
        self.root_folder_path_button = QPushButton(BROWSE_LABEL)
        hbox = QHBoxLayout()
        hbox.addWidget(root_folder_label)
        hbox.addWidget(self.root_folder_path_input)
        hbox.addWidget(self.root_folder_path_button)
        hbox.setSpacing(50)

        title_label = QLabel(COURSE_STRUCTURE_TITLE)
        self.course_structure = CourseStructure(self.application_context)

        vbox.addLayout(hbox)
        vbox.addWidget(title_label)
        vbox.addWidget(self.course_structure)
        right_panel.setLayout(vbox)

        return right_panel

    def create_dashboard(self):
        groupbox = QGroupBox(DASHBOARD_LABEL)
        mini_grid = QGridLayout()

        left_panel = self.create_course_list(groupbox)
        right_panel = self.create_video_tree(groupbox)
        self.action_button = QPushButton(RETRIEVE_COURSES_LABEL)
        self.cancel_button = QPushButton(CANCEL_LABEL)

        mini_grid.addWidget(left_panel, 0, 0, 5, 3)
        mini_grid.addWidget(right_panel, 0, 3, 5, 6)
        mini_grid.addWidget(self.action_button, 5, 7, 1, 1)
        mini_grid.addWidget(self.cancel_button, 5, 8, 1, 1)
        groupbox.setLayout(mini_grid)

        self.grid.addWidget(groupbox, 3, 0, 8, 12)

    def create_progressbar(self):
        groupbox = QGroupBox(PROGRESSBAR_LABEL)
        self.progressbar = QProgressBar(groupbox)
        self.progressbar.setMaximum(PROGRESSBAR_MAXIMUM)
        self.progressbar.setMinimum(PROGRESSBAR_MINIMUM)
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
        if successful:
            self.action_button.setText(RETRIEVE_COURSES_LABEL)
            for _, details in self.session.downloader.courses.items():
                self.course_list.add_course(details)
        else:
            message_box = MessageDialog("Couldn't Login", 
                            "Something went wrong.", CRITICAL, 
                            informativeText="Check your network connection, credentials and try again.")
            message_box.exec_()

    def course_selection_changed(self):
        self.action_button.setText(RETRIEVE_COURSES_LABEL)


    def courses_retrieved(self, successful):
        if successful:
            self.action_button.setText(DOWNLOAD_COURSES_LABEL)
            self.action_button.setEnabled(True)
            for course in self.session.data["selected_courses"]:
                self.course_structure.add_course(self.session.downloader.courses[course])
        
        
    def courses_downloaded(self, successful):
        self.action_button.setText(DOWNLOAD_COURSES_LABEL)
        self.action_button.setEnabled(True)
        if successful:
            self.show_notification()
        elif self.session.cancelled:
            self.cancel_button.setText(CANCEL_LABEL)
            message_box = MessageDialog('Downloads cancelled!', 'Downloads have been cancelled', INFORMATION,
                                        informativeText='To resume download, select the same course and same destination folder. \
                                        Already downloaded files wont be downloaded again')
            message_box.exec_()
        else:
            message_box = MessageDialog('Downloads Interrupted!', 'Downloads have stopped for unknown reason', CRITICAL,
                                        informativeText='To resume download, select the same course and same destination folder. \
                                        Already downloaded files wont be downloaded again')
            message_box.exec_()

            

    def get_root_folder(self):
        file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.root_folder_path_input.setText(file)

    def download_progress(self, fraction_completed):
        self.progressbar.setValue(fraction_completed*PROGRESSBAR_MAXIMUM)

    def cancel_pressed(self):
        self.cancel_button.setText(CANCELLING_LABEL)
        self.session.cancel_pressed()

    def show_notification(self):
        """Show a notification that the Pomodoro has completed one run, and to take a break.
        """
        system_tray_icon = QSystemTrayIcon(self)
        system_tray_icon.show()
        text = 'Download is completed!'
        system_tray_icon.showMessage('Course Downloader', text)

    def raise_error_dialog(self, title, text, message_type=WARNING, informativeText = '', callback=None):
        message_dialog = MessageDialog(title, text, message_type=message_type, informativeText = informativeText, callback=callback)
        message_dialog.exec_()
