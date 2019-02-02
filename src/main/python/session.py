import json
import logging
from pathlib import Path

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QLineEdit

import utils
from constants import (CRITICAL, DOWNLOAD_COURSES_LABEL, INFORMATION, OTHER,
                       PROBLEM, RETRIEVE_COURSES_LABEL, RETRY_LIMIT, VIDEO,
                       WARNING, SESSION_LOG)
from edx_downloader import EdXDownloader

logging.basicConfig(level=logging.DEBUG, filename=SESSION_LOG, filemode="w")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Session(QObject):

    login_successful = pyqtSignal(bool)
    courses_retrieved = pyqtSignal(bool)
    loading_screen = pyqtSignal(bool)
    clear_course_list = pyqtSignal()
    clear_course_structure = pyqtSignal()
    courses_downloaded = pyqtSignal(bool)
    download_progress = pyqtSignal(float)
    destination_required = pyqtSignal(str, str, str)
    course_selection_required = pyqtSignal(str, str, str)

    def __init__(self, configuration, application_context, website_name):
        super().__init__()
        self.configuration = configuration
        self.application_context = application_context
        self.website = website_name
        self.set_downloader(website_name)
        self.data = {"courses": {}, "selected_courses": set(), "lectures": {}}
        self.cancelled = False

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

    @pyqtSlot('QListView', 'QPushButton', 'QLineEdit')
    def action_button_clicked(self, course_list_widget, action_button, root_folder_input):
        if(str(action_button.text()) == RETRIEVE_COURSES_LABEL and len(course_list_widget.selected_courses) > 0):
            action_button.setText(DOWNLOAD_COURSES_LABEL)
            self.retrieve_course_details(course_list_widget)
        elif(str(action_button.text()) == RETRIEVE_COURSES_LABEL):
            self.course_selection_required.emit('Select course(s)',
                                                'Atleast one course has to be selected before trying to retrieve.',
                                                CRITICAL)
        elif(str(action_button.text()) == DOWNLOAD_COURSES_LABEL and root_folder_input.text() != ""):
            action_button.setDisabled(True)
            self.download_courses(course_list_widget, root_folder_input.text())
        elif(str(action_button.text()) == DOWNLOAD_COURSES_LABEL):
            self.destination_required.emit(
                'Select a root folder', 'Destination folder required before downloading.', CRITICAL)

    @pyqtSlot('QLineEdit', 'QLineEdit')
    def login(self, username, password):
        self.clear_course_list.emit()
        self.loading_screen.emit(True)
        self.set_credentials(username.text(), password.text())
        successful = self.downloader.login(self.username, self.password)
        self.loading_screen.emit(False)
        self.login_successful.emit(successful)

    def retrieve_course_details(self, course_list_widget):
        self.clear_course_structure.emit()
        self.loading_screen.emit(True)
        self.data["selected_courses"] = course_list_widget.selected_courses
        successful = self.downloader.get_course_lectures(
            self.data["selected_courses"])
        self.loading_screen.emit(False)
        self.courses_retrieved.emit(successful)

    def cancel_pressed(self):
        self.cancelled = True

    def download_courses(self, course_list_widget, root_folder):
        downloaded = False
        try_count = 0
        download_count = 0
        self.cancelled = False
        self.data["selected_courses"] = course_list_widget.selected_courses

        while ((not downloaded) and try_count < RETRY_LIMIT):
            try:
                for course_id in self.data["selected_courses"]:
                    course_outline = self.downloader.courses[course_id].course_outline
                    for section in course_outline:
                        logger.debug("\tSection name: %s", section)
                        for subsection in course_outline[section]:
                            download_count = self._download_lecture(
                                course_outline, section, subsection, course_id, root_folder, download_count)

                downloaded = True
            except utils.BreakLoop:
                self.courses_downloaded.emit(False)
                return
            except Exception as error:
                logger.error(error)
                try_count = try_count + 1
        self.courses_downloaded.emit(downloaded)

    def _download_lecture(self, course_outline, section, subsection, course_id, root_folder, download_count):
        for index, lecture_url in enumerate(course_outline[section][subsection]):
            path = Path(root_folder, self.downloader.courses[course_id].name,
                        section, subsection)
            lecture_title = (str(index + 1).zfill(len(str(len(course_outline[section][subsection])))) +
                             "-" + course_outline[section][subsection][lecture_url])
            lecture = self.downloader.get_lecture_details(
                lecture_title, lecture_url)
            download_count = download_count + 1

            if lecture is None:
                continue
            downloaded = utils.is_downloaded(
                course_id, section, subsection, self.downloader.courses[course_id], lecture, root_folder)

            if lecture.media_type == VIDEO and (not downloaded):
                lecture = self.downloader.set_lecture_path(
                    lecture_title, lecture_url, path)
                successful = utils.download_lecture(lecture)
                if (successful):
                    lecture = self.downloader.set_lecture_downloaded(
                        lecture_title, lecture_url)
                    utils.save_downloads(
                        course_id, section, subsection, self.downloader.courses[course_id], lecture, root_folder)

                    self.download_progress.emit(
                        download_count/len(self.downloader.lectures))
            else:
                self.download_progress.emit(
                    download_count/len(self.downloader.lectures))

            if self.cancelled:
                raise utils.BreakLoop

        return download_count
