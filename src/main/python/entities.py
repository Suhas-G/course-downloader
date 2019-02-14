from collections import OrderedDict
from constants import VIDEO, BLANK_VALUE, NOT_VIDEO_TEXT, DOWNLOADED_TEXT, NOT_DOWNLOADED_TEXT

class Course(object):
    def __init__(self, name=None, url=None, data_course_key=None,
                 university=None, date=None, course_outline=OrderedDict()):
        """Initialise the course object
        
        Keyword Arguments:
            name {str} -- Name of the course (default: {None})
            url {str} -- URL of the course page (default: {None})
            data_course_key {str} -- Unique ID/key of the course (default: {None})
            university {str} -- University offering the course (default: {None})
            date {str} -- date of the course (starting/ending) (default: {None})
            course_outline {OrderedDict} -- The course structure having sections, subsections and lectures (default: {OrderedDict()})
        """
        self.name = name
        self.url = url
        self.data_course_key = data_course_key
        self.university = university
        self.date = date
        self.course_outline = course_outline

    def __str__(self):
        return ("Course(name={name} ,url={url} ,course_key={data_course_key} ,\
                    university={university} ,date={date})".format(name=self.name, 
                        url=self.url, course_key=self.data_course_key, 
                        university=self.university, date=self.date
        ))


class Lecture(object):
    def __init__(self, title=None, url=None, downloaded=False, media_type=None,
                 download_url=None, from_youtube=False, path=None):
        """Initialise the Lecture object
        
        Keyword Arguments:
            title {str} -- Title of the lecture (default: {None})
            url {[type]} -- URL of the lecture page (default: {None})
            downloaded {bool} -- Flag to indicate if downloaded (default: {False})
            media_type {str} -- Type of lecture: (VIDEO, PROBLEM, OTHER) (default: {None})
            download_url {str} -- URL to the lecture video (default: {None})
            from_youtube {bool} -- Flag to indicate whether the video is from YouTube (default: {False})
            path {Path} -- File path where the video has to be downloaded (default: {None})
        """
        self.title = title
        self.url = url
        self.downloaded = downloaded
        self.media_type = media_type
        self.download_url = download_url
        self.from_youtube = from_youtube
        self.path = path
    
    @property
    def status(self):
        """Return the status of lecture depending on media type and whether its downloaded
        """
        if self.media_type is None:
            return BLANK_VALUE
        elif self.media_type != VIDEO:
            return NOT_VIDEO_TEXT
        elif self.downloaded:
            return DOWNLOADED_TEXT
        else:
            return NOT_DOWNLOADED_TEXT

    def get_dict(self):
        """Convert the attributes to dict
        """
        data = {
            "title": self.title,
            "url": self.url,
            "downloaded": self.downloaded,
            "download_url": self.download_url,
            "path": str(self.path)
        }
        return data

    def __str__(self):
        return ("Lecture(title={title} ,url={url} ,downloaded={downloaded} ,media_type={media_type} \
                ,download_url={download_url} ,from_youtube={from_youtube}, path={path}".format(
            title=self.title, url=self.url, downloaded=self.downloaded, media_type=self.media_type,
            download_url=self.download_url, from_youtube=self.from_youtube, path=self.path
        ))
