import requests
from bs4 import BeautifulSoup
from collections import OrderedDict
from pathlib import Path
import re

from constants import VIDEO, PROBLEM, OTHER, YOUTUBE_URL_PART

from entities import Course, Lecture

import logging
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class EdXDownloader(object):
    def __init__(self, configuration):
        """Initialise the downloader for edX
        
        Arguments:
            configuration {Configuration} -- Configuration object having data about website
        """
        self.configuration = configuration
        self.website_urls = self.configuration.get_website_urls("edX")
        self.session = requests.Session()
        self.session.headers = self.configuration.get_website_headers("edX")
        self.courses = {}
        self.lectures = OrderedDict()

    def login(self, username, password):
        """Login to the edX website
        
        Arguments:
            username {str} -- The username of the user
            password {str} -- The password of the user
        """
        self.username = username
        self.password = password
        login_successful = False
        login_request = self.session.get(self.website_urls["first_url"])

        if(login_request.status_code == 200):
            csrf_token = login_request.cookies["csrftoken"]
            login_request = self.session.post(self.website_urls["login_url"], data={
                                              "email": username, "password": password}, headers={"X-CSRFToken": csrf_token})
            if (login_request.status_code == 200):
                login_successful = self.get_course_list()
            else:
                logger.error("Login unsucessful: %s %s %s", login_request.status_code, login_request.reason, 
                            login_request.text.encode('utf-8'))

        return login_successful

    def get_course_list(self):
        """After logging in, go to user's dashboard and get links to all the courses present
        """
        dashboard = self.session.get(self.website_urls["dashboard_url"])
        self.home_page = BeautifulSoup(dashboard.text, 'html.parser')

        for course_details in self.home_page.select(".wrapper-course-details"):
            course_link = course_details.find(
                                    attrs={"class": "course-target-link"})
            course_university = course_details.find(attrs={"class": "info-university"}) \
                .string.strip("- ")
            course_date = course_details.find(
                                    attrs={"class": "info-date-block"})

            # If any of the data is missing itll probably not be available to download so dont include.
            if None in (course_link, course_university, course_date):
                continue

            if "data-string" in course_date.attrs and "data-datetime" in course_date.attrs:
                date = course_date["data-string"].replace(
                                    "{date}", course_date["data-datetime"].split("T")[0])
            else:
                date = course_date.string.split("-", maxsplit=1)[0] + " " \
                            + course_date.string.split("-", maxsplit=1)[1].strip().split("T")[0]

            course = Course(name=course_link.string, 
                            url=self.website_urls["base_url"] + course_link["href"],
                            data_course_key=course_link["data-course-key"], 
                            university=course_university, date=date)

            self.courses[course_link["data-course-key"]] = course

        if dashboard.status_code == 200:
            return True

        return False

    def get_course_lectures(self, courses):
        """Get all the lectures associated with the selected courses
        
        Arguments:
            courses {Set} -- Set of course IDs
        """
        for course_id in courses:
            url = self.courses[course_id].url
            course_request = self.session.get(url)

            if course_request.status_code != 200:
                return False

            course_page = BeautifulSoup(course_request.text, 'html.parser')
            course_outline = OrderedDict()

            for section in course_page.select("#course-outline-block-tree .section"):
                section_title = section.find(attrs={"class": "section-title"}) \
                    .string.strip()
                
                if section_title is None:
                    continue

                course_outline[section_title] = OrderedDict()
                logger.debug("Section name: %s", section_title)

                for subsection in section.select(".subsection"):
                    subsection_title = subsection.find(
                        attrs={"class": "subsection-title"}).string.strip()

                    if subsection_title is None:
                        continue

                    course_outline[section_title][subsection_title] = OrderedDict()
                    logger.debug("Subsection name: %s", subsection_title)

                    for lecture in subsection.select('a.outline-item'):
                        lecture_title = lecture.find(
                            attrs={"class": "vertical-title"}).string.strip()

                        if lecture_title is None:
                            continue

                        lecture_url = lecture["href"]
                        course_outline[section_title][subsection_title][lecture_url] = lecture_title
                        self.lectures[lecture_url] = Lecture(
                            title=lecture_title, downloaded=False)
                        logger.debug(
                            "Lecture name: %s , Lecture url: %s", lecture_title, lecture_url)

            self.courses[course_id].course_outline = course_outline

        return True

    def get_lecture_details(self, lecture_title, lecture_url):
        """Get details of a rticular lecture
        
        Arguments:
            lecture_title {str} -- Title of the lecture
            lecture_url {str} -- URL of the lecture
        """
        lecture_request = self.session.get(lecture_url)

        if lecture_request.status_code != 200:
            return None

        lecture_page = BeautifulSoup(lecture_request.text, 'html.parser')
        data_id = lecture_url.split("/jump_to/")[-1]
        lecture_classes = lecture_page.find(
            attrs={"data-id": data_id})
            
        if lecture_classes is None:
            return None
            
        lecture_classes = lecture_classes["class"]

        youtube_url = False
        download_url = None

        if VIDEO in lecture_classes:
            lecture_type = VIDEO
            lecture_inner = BeautifulSoup(
                lecture_page.findAll(attrs={"class": "xblock"})[0].text, 'html.parser')

            if lecture_inner is None:
                return None

            download_url = lecture_inner.find(
                attrs={"data-usage-id": data_id}).select_one(".video-download-button")
            youtube_url = False
            if (download_url == None):
                youtube_regex = re.compile(r'streams.*#34[\s\S]*?#34;1.\d*\:(.*?)&#34')
                download_url = re.search(youtube_regex, lecture_page.findAll(attrs={"class": "xblock"})[0].text)
                if not download_url is None:
                    download_url = YOUTUBE_URL_PART + download_url.group(1)
                    youtube_url = True
            else:
                download_url = download_url["href"]

            if download_url is None:
                return None

        elif PROBLEM in lecture_classes:
            lecture_type = PROBLEM
        else:
            lecture_type = OTHER

        lecture = Lecture(lecture_title, lecture_url, downloaded=False, media_type=lecture_type,
                          download_url=download_url, from_youtube=youtube_url, path=None)
        logger.debug("Lecture: %s", str(lecture))
        self.lectures[lecture_url] = lecture

        return self.lectures[lecture_url]

    def set_lecture_downloaded(self, lecture_url):
        """Set the particular lecture as downloaded
        
        Arguments:
            lecture_url {str} -- URL of the lecture
        """
        self.lectures[lecture_url].downloaded = True
        return self.lectures[lecture_url]

    def set_lecture_path(self, lecture_url, path):
        """Set the download path of a particular lecture
        
        Arguments:
            lecture_url {str} -- URL of the lecture
            path {Path} -- Path of the lecture where it'll be downloaded
        """
        self.lectures[lecture_url].path = path
        return self.lectures[lecture_url]
