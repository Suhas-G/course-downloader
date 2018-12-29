from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QStyle, QTreeWidget, QTreeWidgetItem


class CourseStructure(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.courses = []
        self.lectures = []
        self.setHeaderLabel("Courses")

    def add_course(self, course_name, lectures):
        print(course_name)
        course = QTreeWidgetItem(self, [course_name])
        self.addTopLevelItem(course)

        course.setIcon(0, QApplication.style().standardIcon(QStyle.SP_DirIcon))
        self.courses.append(course)
        self.add_lectures(course, lectures)

    def add_lectures(self, course, lectures):
        for lecture in lectures:
            lectureItem = QTreeWidgetItem(course, [lecture])
            lectureItem.setIcon(
                0, QApplication.style().standardIcon(QStyle.SP_DirIcon))
            course.addChild(lectureItem)
