from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QListView


class CourseListView(QListView):
    def __init__(self):
        super().__init__()
        self.model = QStandardItemModel(self)
        self.model.itemChanged.connect(self.course_selection_changed)
        self.setModel(self.model)
        self.courses = {}
        self.selected_courses = set()

    def add_course(self, course_name):
        course_item = QStandardItem(course_name)
        course_item.setCheckable(True)
        self.model.appendRow(course_item)
        self.courses[course_name] = self.model.rowCount()

    def course_selection_changed(self, course_item):
        if course_item.checkState():
            self.selected_courses.add(str(course_item.text()))
        elif(str(course_item.text()) in self.selected_courses):
            self.selected_courses.remove(str(course_item.text()))
