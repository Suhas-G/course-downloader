from collections import OrderedDict


class Course(object):
    def __init__(self, name=None, url=None, data_course_key=None,
                 university=None, date=None, course_outline=OrderedDict()):
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
        self.title = title
        self.url = url
        self.downloaded = downloaded
        self.media_type = media_type
        self.download_url = download_url
        self.from_youtube = from_youtube
        self.path = path

    def get_dict(self):
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
