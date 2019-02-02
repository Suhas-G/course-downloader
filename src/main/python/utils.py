import json
import logging, sys
import re
import subprocess, os
from pathlib import Path
import shlex
import youtube_dl

import requests
from PyQt5.QtWidgets import QFrame

from constants import WINDOWS_EXCLUDED_CHARACTERS

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class QHLine(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class QVLine(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)

class BreakLoop(Exception):
    pass

def is_downloadable(url):
    """
    Does the url contain a downloadable resource
    """
    req = requests.head(url, allow_redirects=True)
    headers = req.headers
    content_type = headers.get('content-type')
    
    if 'text' in content_type.lower():
        return False
    if 'html' in content_type.lower():
        return False
    return True

def get_filename_from_cd(cd):
    """
    Get filename from content-disposition
    """
    if not cd:
        return None
    fname = re.findall('filename=(.+)', cd)
    if len(fname) == 0:
        return None
    return fname[0]

def download_file(url, path, title):
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
    file_path = str(Path(path, title)) + ".%(ext)s"
    ydl_options = {
        'outtmpl': file_path
    }
    with youtube_dl.YoutubeDL(ydl_options) as ydl:
        ydl.download([url])
    print("Downloaded")
    return True


def download_lecture(lecture):
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
    if not Path(path).exists():
        os.makedirs(str(path))


def save_downloads(course_id, section, subsection, course, lecture, root_folder):
    ensure_directory_exists(root_folder)
    if Path(root_folder, "downloads.json").exists():
        with Path(root_folder, "downloads.json").open() as file:
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
    with Path(root_folder, "downloads.json").open(mode="w") as file:
        json.dump(downloads, file, indent=4)

def is_downloaded(course_id, section, subsection, course, lecture, root_folder):
    downloaded = False
    path = Path(root_folder, "downloads.json")
    if path.exists():
        with path.open() as file:
            data = json.load(file)
        
        if course_id in data:
            downloaded = data[course_id]["sections"].get(section, {}) \
                                .get(subsection, {}).get(lecture.url, {}).get("downloaded",False)


    return downloaded



    
