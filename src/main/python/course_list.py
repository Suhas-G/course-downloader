from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QListView


class CourseListView(QListView):
    def __init__(self, application):
        """Initialise the list view to show courses
        
        Arguments:
            application {QApplication} -- Reference to application
        """
        super().__init__()
        self.application = application
        self.model = QStandardItemModel(self)
        self.model.itemChanged.connect(self.course_selection_changed)
        self.setModel(self.model)
        self.courses = {}
        self.selected_courses = set()

    def add_course(self, course):
        """Add a course to the list
        
        Arguments:
            course {Course} -- The course object to be added
        """
        name = course.name + " | " + course.university + " | " + course.date
        course_item = QStandardItem(name)
        course_item.setData({"data-course-key": course.data_course_key})
        course_item.setEditable(False)
        course_item.setCheckable(True)
        self.model.appendRow(course_item)
        self.courses[course.data_course_key] = course

    def course_selection_changed(self, course_item):
        """Callback when any selection of course list changes
        
        If the changed item is checked add to the selected course list
        Arguments:
            course_item {QStandardItem} -- The modified list item
        """
        self.application.course_selection_changed()
        if course_item.checkState():
            self.selected_courses.add(course_item.data()["data-course-key"])
        elif(course_item.data()["data-course-key"] in self.selected_courses):
            self.selected_courses.remove(course_item.data()["data-course-key"])

    def clear_all(self):
        """Clear the course list
        """
        self.model.clear()
