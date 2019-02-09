import json
import logging, sys
import re
import subprocess, os
from pathlib import Path
import shlex
import youtube_dl

import requests
from PyQt5.QtWidgets import QFrame

from constants import WINDOWS_EXCLUDED_CHARACTERS, DOWNLOAD_DATA

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class BreakLoop(Exception):
    """Dummy exception to break out of nested loops
    """
    pass

def is_downloadable(url):
    """Does the url contain a downloadable resource
    
    Arguments:
        url {str} -- URL to check whether it can be downloaded
    """
    req = requests.head(url, allow_redirects=True)
    headers = req.headers
    content_type = headers.get('content-type')
    
    if 'text' in content_type.lower():
        return False
    if 'html' in content_type.lower():
        return False
    return True

def download_file(url, path, title):
    """Download the file
    
    Arguments:
        url {str} -- URL to the file
        path {Path} -- File path to which it'll be downloaded 
        title {str} -- Name of the file
    """
    if is_downloadable(url):
        try:
            req = requests.get(url, allow_redirects=True)
            extension = url.rsplit(".", maxsplit=1)[-1] if "." in url else "mp4"
            with open(str(Path(path, title + "." + extension)), "wb") as file:
                file.write(req.content)
            return True
        except Exception as error:
            logger.error(error)
            return False
    else:
        return False

def download_from_youtube(url, path, title):
    """Download video from youtube using youtube-dl
    Reference: https://rg3.github.io/youtube-dl/
    
    Arguments:
        url {str} -- Youtube URL
        path {Path} -- File path to which it'll be downloaded
        title {str} -- Name of the file
    """
    file_path = str(Path(path, title)) + ".%(ext)s"
    ydl_options = {
        'outtmpl': file_path
    }
    with youtube_dl.YoutubeDL(ydl_options) as ydl:
        ydl.download([url])
    return True


def download_lecture(lecture):
    """Util method to download the lecture.
    Checks whether its a file URL or if its YouTube link and calls appropriate function
    
    Arguments:
        lecture {Lecture} -- The Lecture object having required details
    """
    url = lecture.download_url
    path = Path(lecture.path.parts[0], *[re.sub('[' + WINDOWS_EXCLUDED_CHARACTERS + ']', '', part) for part in lecture.path.parts[1:]])
    title = re.sub('[' + WINDOWS_EXCLUDED_CHARACTERS + ']', '', lecture.title)
    logger.debug("Saving %s to %s", title, path)
    ensure_directory_exists(path)
    if lecture.from_youtube:
        successful = download_from_youtube(url, path, title)
    else:
        successful = download_file(url, path, title)

    return successful

def ensure_directory_exists(path):
    """Util method to check whether the path exists and if not make necessary directories
    
    Arguments:
        path {str} -- Path to be checked
    """
    if not Path(path).exists():
        os.makedirs(str(path))


def save_downloads(course_id, section, subsection, course, lecture, root_folder):
    """Util method to save the state of the downloads in a JSON file
    
    Arguments:
        course_id {str} -- Course ID of the lecture
        section {str} -- Section of the lecture
        subsection {str} -- Subsection of the lecture
        course {Course} -- Selected Course object having all its details
        lecture {Lecture} -- Downloaded Lecture object having all its details
        root_folder {str} -- The destination folder selected for the downloads
    """
    ensure_directory_exists(root_folder)
    if Path(root_folder, DOWNLOAD_DATA).exists():
        with Path(root_folder, DOWNLOAD_DATA).open() as file:
            downloads = json.load(file)
    else:
        downloads = {
            course_id: {
                "name": course.name,
                "sections": {
                    section : {
                        subsection: {}
                    }
                }
            }}
    lecture_data = lecture.get_dict()
    course_data = downloads.get(course_id, {})
    course_data["sections"] = course_data.get("sections", {})
    course_data["sections"][section] = course_data["sections"].get(section, {})
    course_data["sections"][section][subsection] = course_data["sections"][section].get(subsection, {})
    course_data["sections"][section][subsection][lecture.url] = lecture_data
    downloads[course_id] = course_data
    with Path(root_folder, DOWNLOAD_DATA).open(mode="w") as file:
        json.dump(downloads, file, indent=4)

def is_downloaded(course_id, section, subsection, course, lecture, root_folder):
    """util method to check if the lecture has already been downloaded
    
    Arguments:
        course_id {str} -- Course ID of the lecture
        section {str} -- Section of the lecture
        subsection {str} -- Subsection of the lecture
        course {Course} -- Selected Course object having all its details
        lecture {Lecture} -- Downloaded Lecture object having all its details
        root_folder {str} -- The destination folder selected for the downloads
    """
    downloaded = False
    path = Path(root_folder, DOWNLOAD_DATA)
    if path.exists():
        with path.open() as file:
            data = json.load(file)
        
        if course_id in data:
            downloaded = data[course_id]["sections"].get(section, {}) \
                                .get(subsection, {}).get(lecture.url, {}).get("downloaded",False)


    return downloaded



    
